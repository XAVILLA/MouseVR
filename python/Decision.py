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


class Decision:
    def __init__(self,ard):
        self.ard = ard
        self.ard.start()
    

    
    """
    Main function. Will start experiment as specified in the configFile passed in the argument.
    """
    def startExperiment(self, trialName,numOfTrials,configFile,isDebug=False):
        if isDebug:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.CRITICAL)
        logging.info("Started arduino reader")
        if not self.ard.isAlive():
            raise Exception("Hardware reading process is dead. Try rerunning the whole program")

        self.ard.write("quiet")
        waitVisualInit = 3

        #Reading files and config
        self.mainFolder = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__),"../Decision")))
        self.dataFolder = os.path.join(self.mainFolder,'data')
        self.imageFolder = os.path.join(self.mainFolder,'images')
        
        

        configFilePath = configFile
        configFileNameNoExt = os.path.splitext(os.path.basename(configFile))[0]
        if not os.path.isfile(configFilePath):
            raise ValueError("Config file {} not found".format(configFilePath))
        with open(configFilePath) as f:
            args = json.load(f)
        isPositiveFilter = lambda x : x > 0
        isNonNegativeFilter = lambda x : x >= 0
        is0to1 = lambda x : x >= 0 and x <= 1
        self.ruleAImgLocation = args["Rule A image files"]
        Utilities.checkInput(self.ruleAImgLocation,list)
        [Utilities.checkInput(img,str) for img in self.ruleAImgLocation]
        self.ruleBImgLocation = args["Rule B image files"]
        Utilities.checkInput(self.ruleBImgLocation,list)
        [Utilities.checkInput(img,str) for img in self.ruleBImgLocation]
        self.ruleAFreq = args["Rule A Frequency"]
        Utilities.checkInput(1.0*self.ruleAFreq,float,isPositiveFilter)
        self.ruleBFreq = args["Rule B Frequency"]
        Utilities.checkInput(1.0*self.ruleBFreq,float,isPositiveFilter)
        self.stimAImgLocation = args["Stimulus A image files"]
        Utilities.checkInput(self.stimAImgLocation,list)
        [Utilities.checkInput(img,str) for img in self.stimAImgLocation]
        self.stimBImgLocation = args["Stimulus B image files"]
        Utilities.checkInput(self.stimBImgLocation,list)
        [Utilities.checkInput(img,str) for img in self.stimBImgLocation]
        self.stimAFreq = args["Stimulus A Frequency"]
        Utilities.checkInput(1.0*self.stimAFreq,float,isPositiveFilter)
        self.stimBFreq = args["Stimulus B Frequency"]
        Utilities.checkInput(1.0*self.stimBFreq,float,isPositiveFilter)
        Utilities.checkInput(numOfTrials,int,isPositiveFilter)
        self.fov = args["Field of view degree"]
        Utilities.checkInput(1.0*self.fov,float,isPositiveFilter)
        self.ruleAProb = args["Rule A probability"]
        Utilities.checkInput(1.0*self.ruleAProb,float,is0to1)
        self.stimAProb = args["Stimulus A probability"]
        Utilities.checkInput(1.0*self.stimAProb,float,is0to1)
        self.isSoundRule = args["Is Sound for Rule"]
        Utilities.checkInput(self.isSoundRule,[0,1])
        self.isSoundStim = args["Is Sound for Stimulus"]
        Utilities.checkInput(self.isSoundStim,[0,1])
        self.distance = args["Monitor distance"]
        Utilities.checkInput(1.0*self.distance,float,isPositiveFilter)
        self.monitorSize = args["Monitor size"]
        Utilities.checkInput(1.0*self.monitorSize,float,isPositiveFilter)
        self.isShock = args["Give shock"]
        Utilities.checkInput(self.isShock,[0,1])
        self.tRule = 1.0*args["Rule duration"]
        Utilities.checkInput(1.0*self.tRule,float,isNonNegativeFilter)
        self.tDelay = args["Delay duration"]
        Utilities.checkInput(1.0*self.tDelay,float,isNonNegativeFilter)
        self.tStimulus = 1.0*args["Stimulus duration"]
        Utilities.checkInput(1.0*self.tStimulus,float,isNonNegativeFilter)
        self.tCorrectVisual = 1.0*args["Correct response visual duration"]
        Utilities.checkInput(self.tCorrectVisual,float,isNonNegativeFilter)
        self.tCorrectSound = 1.0*args["Correct response sound duration"]
        Utilities.checkInput(self.tCorrectSound,float,isNonNegativeFilter)
        self.tWrongFlash = 1.0*args["Wrong response flash duration"]
        Utilities.checkInput(self.tWrongFlash,float,isNonNegativeFilter)
        self.tWrongRest = 1.0*args["Wrong response rest duration"]
        Utilities.checkInput(self.tWrongRest,float,isNonNegativeFilter)
        self.tWrongSound  = 1.0*args["Wrong response sound duration"]
        Utilities.checkInput(self.tWrongSound,float,isNonNegativeFilter)
        logging.info("JSON Loaded")
        #Image file names formatting
        self.ruleAImgNames = []
        self.ruleBImgNames = []
        if not self.isSoundRule:
            for f in self.ruleAImgLocation:
                fPath = os.path.join(self.imageFolder,f)
                if os.path.isdir(fPath):
                    relFilePaths = Utilities.findFiles(fPath,[".jpg",".jpeg",".png"],False)
                    self.ruleAImgNames.extend([os.path.join(f,i) for i in relFilePaths])
                else:
                    self.ruleAImgNames.extend([f])
            for f in self.ruleBImgLocation:
                fPath = os.path.join(self.imageFolder,f)
                if os.path.isdir(fPath):
                    relFilePaths = Utilities.findFiles(fPath,[".jpg",".jpeg",".png"],False)
                    self.ruleBImgNames.extend([os.path.join(f,i) for i in relFilePaths])
                else:
                    self.ruleBImgNames.extend([f])
            logging.info("Rule A Images Found and loaded : {}".format(self.ruleAImgNames))
            logging.info("Rule B Images Found and loaded : {}".format(self.ruleBImgNames))
        self.ruleAImagesFull = [os.path.join(self.imageFolder,imgFile) for imgFile in self.ruleAImgNames]
        self.ruleBImagesFull = [os.path.join(self.imageFolder,imgFile) for imgFile in self.ruleBImgNames]
        self.stimAImgNames = []
        self.stimBImgNames = []
        if not self.isSoundStim:
            for f in self.stimAImgLocation:
                fPath = os.path.join(self.imageFolder,f)
                if os.path.isdir(fPath):
                    relFilePaths = Utilities.findFiles(fPath,[".jpg",".jpeg",".png"],False)
                    self.stimAImgNames.extend([os.path.join(f,i) for i in relFilePaths])
                else:
                    self.stimAImgNames.extend([f])
            for f in self.stimBImgLocation:
                fPath = os.path.join(self.imageFolder,f)
                if os.path.isdir(fPath):
                    relFilePaths = Utilities.findFiles(fPath,[".jpg",".jpeg",".png"],False)
                    self.stimBImgNames.extend([os.path.join(f,i) for i in relFilePaths])
                else:
                    self.stimBImgNames.extend([f])
            logging.info("Stimulus A Images Found and loaded : {}".format(self.stimAImgNames))
            logging.info("Stimulus B Images Found and loaded : {}".format(self.stimBImgNames))
        self.stimAImagesFull = [os.path.join(self.imageFolder,imgFile) for imgFile in self.stimAImgNames]
        self.stimBImagesFull = [os.path.join(self.imageFolder,imgFile) for imgFile in self.stimBImgNames]

        date = datetime.datetime.now()
        fileName = "{}_{}_{}".format(date.strftime("%Y%m%d-%H%M"),configFileNameNoExt,trialName)
        if not os.path.exists(self.dataFolder):
            raise Exception("Folder {} not found".format(self.dataFolder))
        dataFile = os.path.join(self.dataFolder,fileName)
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
        self.visual = Visual(self.stimAImagesFull + self.stimBImagesFull + self.ruleAImagesFull + self.ruleBImagesFull,self.monitorSize,self.distance,not isDebug)
        self.visual.start()
        time.sleep(waitVisualInit)
        with open(dataFileCSV,'w',newline='\n',encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile,delimiter=',',quoting=csv.QUOTE_MINIMAL)
            try:
                with open(dataFileJSON,'w') as f:
                    json.dump(args,f,sort_keys=True)
            except:
                raise Exception("Could not save JSON file to {}".format(configFilePath,dataFileJSON))
            for trial in range(numOfTrials):
                lickTime = 0
                logging.info("Trial: {}".format(trial+1))
                rule = self.showRule()
                time.sleep(self.tDelay)
                visualStartTime = time.time()
                stim = self.showStim()
                if self.isLick(self.tStimulus):
                    lickTime = time.time()-visualStartTime 
                    logging.info("Lick time: {}".format(lickTime))
                    if (rule and stim) or (not rule and not stim):
                        #Correct
                        logging.info("Correct")
                        Sound.correct(self.tCorrectSound)
                        self.visual.cancelAll()
                        self.ard.deliverReward()
                        time.sleep(self.tCorrectVisual)
                    else:
                        #Wrong
                        logging.info("Wrong")
                        self.visual.wrong(self.tWrongFlash,self.tWrongRest)
                        Sound.wrong(self.tWrongSound)
                        if self.isShock:
                            self.ard.deliverShock()
                        time.sleep(self.tWrongFlash+self.tWrongRest)
                else:
                    logging.info("No lick")
                    if (rule and not stim) or (not rule and stim):
                        logging.info("Correct")
                        #Correct
                        Sound.correct(self.tCorrectSound)
                        self.visual.cancelAll()
                        self.ard.deliverReward()
                        time.sleep(self.tCorrectVisual)
                    else:
                        #Wrong
                        logging.info("Wrong")
                        self.visual.wrong(self.tWrongFlash,self.tWrongRest)
                        Sound.wrong(self.tWrongSound)
                        if self.isShock:
                            self.ard.deliverShock()
                        time.sleep(self.tWrongFlash+self.tWrongRest)
                writer.writerow([rule,stim,lickTime])
        self.visual.close()

    def showRule(self):
        isRuleA = Utilities.pickByWeight([1-self.ruleAProb,self.ruleAProb])                
        if self.isSoundRule:
            freq = self.ruleAFreq if isRuleA else self.ruleBFreq
            Sound.playFreq(freq,self.tRule)
            logging.info("Sending Sound {} for Rule {}".format(freq,'A' if isRuleA else 'B'))
        else:
            nextImg = Utilities.choice(self.ruleAImgNames if isRuleA else self.ruleBImgNames)
            nextImgFull = os.path.join(self.imageFolder,nextImg)
            self.visual.show(nextImgFull,self.fov,[0.5,0.5],self.tRule)
            logging.info("Sending Visual {} for Rule {}".format(nextImg,'A' if isRuleA else 'B'))
        return isRuleA
        
    def showStim(self):
        isStimA = Utilities.pickByWeight([1-self.stimAProb,self.stimAProb])                
        if self.isSoundStim:
            freq = self.stimAFreq if isStimA else self.stimBFreq
            Sound.playFreq(freq,self.tStimulus)
            logging.info("Sending Sound {} for Stimulus {}".format(freq,'A' if isStimA else 'B'))
        else:
            nextImg = Utilities.choice(self.stimAImgNames if isStimA else self.stimBImgNames)
            nextImgFull = os.path.join(self.imageFolder,nextImg)
            self.visual.show(nextImgFull,self.fov,[0.5,0.5],self.tStimulus)
            logging.info("Sending Visual {} for Stimulus {}".format(nextImg,'A' if isStimA else 'B'))
        return isStimA
        
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
        
        

