from Visual import Visual
from MouseArduino import MouseArduino
import queue
import time
import Utilities
import Sound
import logging
import os
import datetime
import csv
import json


class ABSingleLick:
    def __init__(self,ard):
        self.ard = ard
        self.ard.start()
    

    
    """
    Main function. Will start experiment as specified in the configFile passed in the argument.
    There are three folders of interest this function will access.
    ~/Desktop/AppleBanana/images : Folder for image files. In the config, you can pass in folder or file name. 
                                    Passing in folder name will read all images in that folder.
    ~/Desktop/AppleBanana/data : Folder where the data will be saved. The file name is <date>_<trialName>.csv
                                It will be in csv format 
                                "<Image-name>,<1 if A-image, 0 if B-image>,<Lick time in seconds>,<fov>,<Relative x Coordinates>,<Relative y Coordinates>"
                                example of one row : "A/image1.jpg,1,1.2,8,0.5,0.5"
    """
    def startExperiment(self, trialName,numOfTrials,configFile):
        logging.info("Started arduino reader")
        if not self.ard.isAlive():
            raise Exception("Hardware reading process is dead. Try rerunning the whole program")

        self.ard.write("quiet")
        waitVisualInit = 3

        #Reading files and config
        mainFolder = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__),"../AppleBanana")))
        dataFolder = os.path.join(mainFolder,'data')
        imageFolder = os.path.join(mainFolder,'images')
        

        configFilePath = configFile
        configFileNameNoExt = os.path.splitext(os.path.basename(configFile))[0]
        if not os.path.isfile(configFilePath):
            raise ValueError("Config file {} not found".format(configFilePath))
        with open(configFilePath) as f:
            args = json.load(f)
        isPositiveFilter = lambda x : x > 0
        isNonNegativeFilter = lambda x : x >= 0
        is0to1 = lambda x : x >= 0 and x <= 1
        aImgLocation = args["A image files"]
        Utilities.checkInput(aImgLocation,list)
        [Utilities.checkInput(img,str) for img in aImgLocation]
        bImgLocation = args["B image files"]
        Utilities.checkInput(bImgLocation,list)
        [Utilities.checkInput(img,str) for img in bImgLocation]
        Utilities.checkInput(numOfTrials,int,isPositiveFilter)
        aProb = args["A image probability"]
        Utilities.checkInput(1.0*aProb,float,is0to1)
        distance = args["Monitor distance"]
        Utilities.checkInput(1.0*distance,float,isPositiveFilter)
        monitorSize = args["Monitor size"]
        Utilities.checkInput(1.0*monitorSize,float,isPositiveFilter)
        fovDegrees = args["Field of view degrees"]
        Utilities.checkInput(fovDegrees,list)
        [Utilities.checkInput(1.0*factor,float,isPositiveFilter) for factor in fovDegrees]
        fovDegreesWeights = args["Field of view weights"]
        Utilities.checkInput(fovDegreesWeights,list)
        [Utilities.checkInput(1.0*w,float,isPositiveFilter) for w in fovDegreesWeights]
        if len(fovDegrees) != len(fovDegreesWeights):
            raise ValueError("From JSON config file, Field of view degrees and Field of view weights don't have same number of elements")
        relativeCoordinates = args["Relative coordinates"]
        Utilities.checkInput(relativeCoordinates,list)
        [Utilities.checkInput(1.0*c[0],float,is0to1) for c in relativeCoordinates]
        [Utilities.checkInput(1.0*c[1],float,is0to1) for c in relativeCoordinates]
        relativeCoordinatesWeights = args["Relative coordinates weights"]
        Utilities.checkInput(relativeCoordinatesWeights,list)
        [Utilities.checkInput(1.0*w,float,isPositiveFilter) for w in relativeCoordinatesWeights]
        if len(relativeCoordinates) != len(relativeCoordinatesWeights):
            raise ValueError("From JSON config file, Relative coordinates and Relative coordinates weights don't have same number of elements")
        isRewardFirst = args["Give reward without lick"]
        Utilities.checkInput(isRewardFirst,[0,1])
        isShock = args["Give shock"]
        Utilities.checkInput(isShock,[0,1])
        tCue = 1.0*args["Cue duration"]
        Utilities.checkInput(tCue,float,isNonNegativeFilter)
        tCueSound = 1.0*args["Cue sound duration"]
        Utilities.checkInput(tCueSound,float,isNonNegativeFilter)
        tStimulus = 1.0*args["Stimulus duration"]
        Utilities.checkInput(tStimulus,float,isNonNegativeFilter)
        tCorrectVisual = 1.0*args["Correct response visual duration"]
        Utilities.checkInput(tCorrectVisual,float,isNonNegativeFilter)
        tCorrectSound = 1.0*args["Correct response sound duration"]
        Utilities.checkInput(tCorrectSound,float,isNonNegativeFilter)
        tWrongFlash = 1.0*args["Wrong response flash duration"]
        Utilities.checkInput(tWrongFlash,float,isNonNegativeFilter)
        tWrongRest = 1.0*args["Wrong response rest duration"]
        Utilities.checkInput(tWrongRest,float,isNonNegativeFilter)
        tWrongSound  = 1.0*args["Wrong response sound duration"]
        Utilities.checkInput(tWrongSound,float,isNonNegativeFilter)

        #Image file names formatting
        aImgNames = []
        bImgNames = []
        for f in aImgLocation:
            fPath = os.path.join(imageFolder,f)
            if os.path.isdir(fPath):
                relFilePaths = Utilities.findFiles(fPath,[".jpg",".jpeg",".png"],False)
                aImgNames.extend([os.path.join(f,i) for i in relFilePaths])
            else:
                aImgNames.extend([f])
        for f in bImgLocation:
            fPath = os.path.join(imageFolder,f)
            if os.path.isdir(fPath):
                relFilePaths = Utilities.findFiles(fPath,[".jpg",".jpeg",".png"],False)
                bImgNames.extend([os.path.join(f,i) for i in relFilePaths])
            else:
                bImgNames.extend([f])
        aImgNamesFull = [os.path.join(imageFolder,imgFile) for imgFile in aImgNames]
        bImgNamesFull = [os.path.join(imageFolder,imgFile) for imgFile in bImgNames]


        date = datetime.datetime.now()
        fileName = "{}_{}_{}".format(date.strftime("%Y%m%d-%H%M"),configFileNameNoExt,trialName)
        if not os.path.exists(dataFolder):
            raise Exception("Folder {} not found".format(dataFolder))
        dataFile = os.path.join(dataFolder,fileName)
        dataFileCSV = dataFile + ".csv"
        dataFileJSON = dataFile + ".json"

        #add number to fileName if file already exists
        if os.path.exists(dataFileCSV):
            i = 1
            dataFileNum = dataFile + str(i)
            dataFileCSV = dataFileNum + ".csv"
            dataFileJSON = dataFileNum + ".json"
            while os.path.exists(dataFileCSV):
                i += 1
                dataFileNum = dataFile + str(i)
                dataFileCSV = dataFileNum + ".csv"
                dataFileJSON = dataFileNum + ".json"

        #Start Experiment
        logging.info("Starting Visual")
        visual = Visual(aImgNamesFull + bImgNamesFull,monitorSize,distance)
        visual.start()
        time.sleep(waitVisualInit)
        with open(dataFileCSV,'w',newline='\n',encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile,delimiter=',',quoting=csv.QUOTE_MINIMAL)
            try:
                with open(dataFileJSON,'w') as f:
                    json.dump(args,f,sort_keys=True)
            except:
                raise Exception("Could not save JSON file to {}".format(configFilePath,dataFileJSON))
            lastImg = None
            lastCoord = None
            lastFov = None
            isCorrectImage = None
            def nextStim():
                fov = fovDegrees[Utilities.pickByWeight(fovDegreesWeights)]
                coord = relativeCoordinates[Utilities.pickByWeight(relativeCoordinatesWeights)]
                isCorrectImage = Utilities.pickByWeight([1-aProb,aProb])
                if isCorrectImage:
                    nextImg = Utilities.choice(aImgNames)
                else:
                    nextImg = Utilities.choice(bImgNames)
                return (nextImg,isCorrectImage,fov,coord)
            for trial in range(numOfTrials):
                lickTime = 0
                logging.debug("Trial {}".format(trial+1))
                logging.info("Starting Cue")
                Sound.cue(tCueSound)
                visual.cue() 
                time.sleep(tCue)
                nextImg,isCorrectImage,fov,coord = nextStim()
                while (nextImg == lastImg and  coord == lastCoord and fov == lastFov):
                    nextImg,isCorrectImage,fov,coord = nextStim()
                lastImg = nextImg
                lastCoord = coord
                lastFov = fov
                nextImgFull = os.path.join(imageFolder,nextImg)
                logging.info("Showing {} image {}".format("Correct" if isCorrectImage else "B",nextImg))
                logging.info("FOV: {} Coordinate: {}".format(fov,coord))

                #Visual stimulus Start
                visual.show(nextImgFull,fov,coord,tStimulus)
                visualStartTime = time.time()
                if isRewardFirst and isCorrectImage:
                    #For Phase 1 reward association task. Give reward if it is A-Image
                    self.ard.deliverReward()
                    Sound.correct(tCorrectSound)
                    if self.isLick(tStimulus):
                        lickTime = time.time()-visualStartTime
                        time.sleep(max(visualStartTime+tStimulus - time.time(),0))
                elif self.isLick(tStimulus):
                    lickTime = time.time()-visualStartTime 
                    if isCorrectImage:
                        #Lick & A-Image
                        logging.info("(GOOD)A-Lick")
                        Sound.correct(tCorrectSound)
                        visual.show(nextImgFull,fov,coord,tCorrectVisual)
                        self.ard.deliverReward()
                        time.sleep(tCorrectVisual)
                    else:
                        #Lick & B-Image
                        logging.info("(BAD)B-Lick")
                        visual.wrong(tWrongFlash,tWrongRest)
                        Sound.wrong(tWrongSound)
                        if isShock:
                            self.ard.deliverShock()
                        time.sleep(tWrongFlash+tWrongRest)
                else:
                    if isCorrectImage:
                        #No Lick & A-Image
                        logging.info("(BAD)A-No Lick")
                        visual.wrong(tWrongFlash,tWrongRest)
                        Sound.wrong(tWrongSound)
                        if isShock:
                            self.ard.deliverShock()
                        time.sleep(tWrongFlash+tWrongRest)
                    else:
                        #No Lick & B-Image
                        logging.info("(GOOD)B-No Lick")
                        pass
                writer.writerow([nextImg,isCorrectImage*1,lickTime,fov,coord])
        visual.close()

        
    #"""
    #Check lick until it reaches timeout and return True. False if timeout reached
    #Checks message is 'LK'
    #"""
    #def isLick(self,timeout):
    #    logging.debug("Checking Lick")
    #    self.ard.clearQueue()
    #    start = time.time()
    #    if not self.ard.newMsg.wait(timeout):
    #        return False
    #    else:
    #        while time.time()-start < timeout:
    #                if not self.ard.msgQueue.empty():
    #                    msg = self.ard.msgQueue.get()
    #                    args = Utilities.parse(msg)
    #                    if args[1].strip() == 'LK':
    #                        logging.info("LICK")
    #                        return True
    #    logging.info("NOLICK")
    #    return False
    """  
    Check lick until it reaches timeout and return True. False if timeout reached  
    Does not check message is 'LK'. Uses MouseArduino's eventOnly variable
    The arduino must send only 'LK' string for this to work.
    """
    def isLick(self,timeout):
        self.ard.clearQueue()
        start = time.time()
        return self.ard.newMsg.wait(timeout)
        
        

