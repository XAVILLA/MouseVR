from tkinter import Tk,Label,Button,Entry,Frame,filedialog,messagebox,Checkbutton,StringVar,BooleanVar,IntVar
import tkinter as tk
from MouseArduino import MouseArduino
from Decision import Decision
import json
import sys
import threading
import Utilities
import os
import time
import Sound

LARGE_FONT = ("Verdana", 11)
BACKGROUND_COLOR = '#e1d5ce'
HEADER_COLOR = '#e0a989'
LABEL_COLOR = '#2cc7a0'
TEXT_FONT = 'helvetica 9 bold'
LICK_OFF_COLOR= '#6b6b6b'
LICK_FONT = 'Verdana 40 bold'
ON_COLOR = 'green'
OFF_COLOR = 'red'
STATUS_FONT = 'Verdana 15 bold'
class DecisionGui:
    def __init__(self,root=Tk()):
        self.root = root
        self.root.title("Decision Experiment")
        self.root.configure(bg=BACKGROUND_COLOR)
        self.titleLabel = Label(self.root,text='Decision Experiment',font=STATUS_FONT,bg=BACKGROUND_COLOR)
        self.ard = None
        self.experiment = None
        self.isConfigLoaded = False
        self.isArdConnected = False
        self.isPumpOn = False
        self.estTime = StringVar()
        self.lickCount = IntVar()
        self.lickCount.set(0)
        self.isSoundOn = BooleanVar()
        self.stopUpdating = threading.Event()
        self.ardUpdater = threading.Thread(target=self.updateVariable)
        port = MouseArduino.getUnoPort()


        #Frames
        self.master = Frame(root,bg=BACKGROUND_COLOR)
        self.master.grid_rowconfigure(0)
        self.master.grid_rowconfigure(1)
        self.master.grid_rowconfigure(2, weight=5)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1)
        self.ardInitFrame = Frame(self.master,bd=3,relief='groove',bg=BACKGROUND_COLOR)
        self.ardControlFrame = Frame(self.master,bd=3,relief='groove',bg=BACKGROUND_COLOR)
        self.initFrame = Frame(self.master,bd=3,relief='groove',bg=BACKGROUND_COLOR)
        self.argFrame = Frame(self.master,bd=3,relief='groove',bg=BACKGROUND_COLOR)
        self.finalControlFrame = Frame(self.master,bd=3,relief='groove',bg=BACKGROUND_COLOR)


        #ardInitFrame
        self.ardInitFrameLabel = Label(self.ardInitFrame,text="Connect to Hardware",bg=HEADER_COLOR,font=LARGE_FONT,fg='black',borderwidth=2,width=40)
        self.comLabel = Label(self.ardInitFrame,bg=BACKGROUND_COLOR,text="Com Port:",font=TEXT_FONT)
        self.comEntry = Entry(self.ardInitFrame,font=TEXT_FONT)
        self.baudrateLabel = Label(self.ardInitFrame,bg=BACKGROUND_COLOR,text="Baudrate:",font=TEXT_FONT)
        self.baudrateEntry = Entry(self.ardInitFrame,font=TEXT_FONT)
        self.connectButton = Button(self.ardInitFrame,text="Connect",font=STATUS_FONT,command=self.connect)
        self.ardInitFrameLabel.grid(row=0,columnspan=2,padx=40,pady=10)
        self.comLabel.grid(row=1,column=0,sticky=tk.E)
        self.comEntry.grid(row=1,column=1,sticky=tk.W)
        self.baudrateLabel.grid(row=2,column=0,sticky=tk.E)
        self.baudrateEntry.grid(row=2,column=1,sticky=tk.W)
        self.connectButton.grid(row=3,columnspan=2,pady=10)
        self.comEntry.insert(0,port)
        self.baudrateEntry.insert(0,115200)
        
        #ardControlFrame
        self.ardControlFrameLabel = Label(self.ardControlFrame,text='Pre-experiment Control',bg=HEADER_COLOR,font=LARGE_FONT,fg='black',borderwidth=2,width=40)
        self.sendStringEntry = Entry(self.ardControlFrame,font=TEXT_FONT,width=20)
        self.sendStringButton = Button(self.ardControlFrame,text='Send String',font=TEXT_FONT,bg=BACKGROUND_COLOR,command=self.sendString)
        self.rewardButton = Button(self.ardControlFrame,text='Reward(R)',font=STATUS_FONT,width=10,bg=BACKGROUND_COLOR,command=self.deliverReward,height=1)
        self.pumpButton = Button(self.ardControlFrame,text='Pump Water(P)',font=STATUS_FONT,command=self.togglePump,bg=OFF_COLOR,width=12,height=1)
        self.lickLabel = Label(self.ardControlFrame,text='LICK',bg=LICK_OFF_COLOR,font=LICK_FONT,width=10,height=1)
        self.lickCountLabel = Label(self.ardControlFrame,text='Lick Count :',bg=BACKGROUND_COLOR,font=LARGE_FONT)
        self.lickCountButton = Button(self.ardControlFrame,textvariable=self.lickCount,font=LARGE_FONT,bg=BACKGROUND_COLOR,command=lambda : self.lickCount.set(0))
        self.soundCheckButton = Checkbutton(self.ardControlFrame,text='Lick Sound',variable=self.isSoundOn,bg=BACKGROUND_COLOR)

        self.ardControlFrameLabel.grid(row=0,columnspan=2,padx=40,pady=10)
        self.sendStringEntry.bind('<Return>',self.sendString)
        self.sendStringEntry.grid(row=1,column=0,padx=5,sticky=tk.E)
        self.sendStringEntry.bind('<Escape>',lambda x: self.master.focus())
        self.sendStringButton.grid(row=1,column=1,padx=5,sticky=tk.W)
        self.rewardButton.grid(row=2,column=0,pady=10)
        self.pumpButton.grid(row=2,column=1,pady=10)
        self.lickLabel.grid(row=3,columnspan=2,pady=15)
        self.lickCountLabel.grid(row=4,column=0,sticky=tk.E)
        self.lickCountButton.grid(row=4,column=1,sticky=tk.W)
        self.soundCheckButton.grid(row=5,columnspan=2)

        #initFrame
        self.initFrameLabel = Label(self.initFrame,text="Session Configuration",font=LARGE_FONT,bg=HEADER_COLOR,fg='black',borderwidth=2,width=40)
        self.loadButton = Button(self.initFrame,text="Load Config(L)",font=STATUS_FONT,command=self.selectFile)
        self.sessionNameLabel = Label(self.initFrame,text="Session Name:",font=TEXT_FONT,bg=BACKGROUND_COLOR)
        self.sessionNameEntry = Entry(self.initFrame,font=TEXT_FONT)
        self.numOfTrialsLabel = Label(self.initFrame,text="Number of Trials:",font=TEXT_FONT,bg=BACKGROUND_COLOR)
        self.numOfTrialsEntry = Entry(self.initFrame,font=TEXT_FONT)
        self.numOfTrialsEntry.bind('<KeyRelease>',self.updateTime)
        self.numOfTrialsEntry.bind('<Escape>',lambda x: self.master.focus())
        self.initFrameLabel.grid(row=0,columnspan=2,padx=40,pady=10)
        self.sessionNameLabel.grid(row=1,column=0,sticky=tk.E)
        self.sessionNameEntry.grid(row=1,column=1,sticky=tk.W)
        self.sessionNameEntry.bind('<Escape>',lambda x: self.master.focus())
        self.numOfTrialsLabel.grid(row=2,column=0,sticky=tk.E)
        self.numOfTrialsEntry.grid(row=2,column=1,sticky=tk.W)
        self.loadButton.grid(row=3,columnspan=2,pady=10)

        #finalControlFrame
        self.finalControlFrameLabel = Label(self.finalControlFrame,text='Experiment Control',bg=HEADER_COLOR,font=LARGE_FONT,fg='black',bd=2,width=40)
        self.estTimeLabel = Label(self.finalControlFrame,textvariable=self.estTime,font=STATUS_FONT,bg=BACKGROUND_COLOR)
        self.startButton = Button(self.finalControlFrame,text="START EXPERIMENT",font='Helvetica 20 bold',command=self.startExperiment)
        self.finalControlFrameLabel.grid(padx=40,pady=10)
        self.estTimeLabel.grid(pady=10)
        self.startButton.grid(pady=15)



        #master
        self.titleLabel.pack(pady = 5)
        self.master.pack(padx=20,pady=20)
        self.initFrame.grid(row=0,column=0)
        self.ardInitFrame.grid(row=1,column=0)
        self.finalControlFrame.grid(row=2,column=0,sticky='NSWE')
        self.argFrame.grid(row=0,column=1,rowspan=3,sticky='NSWE')
        for frame in [self.master,self.initFrame,self.ardInitFrame,self.finalControlFrame,self.argFrame]:
            frame.bind('r',self.deliverReward)
            frame.bind('p',self.togglePump)
            frame.bind('l',self.selectFile)
            frame.bind('R',self.deliverReward)
            frame.bind('P',self.togglePump)
            frame.bind('L',self.selectFile)
            frame.bind("<Button-1>",lambda e: self.master.focus_set())
        self.updateTime()





    def run(self):
        self.master.mainloop()
        
    def selectFile(self,event=None):
        fileName = filedialog.askopenfilename() 
        self.configFileName = fileName
        for widget in self.argFrame.winfo_children():
            widget.destroy()
        self.argFrameLabel = Label(self.argFrame,text="Experiment Configuration: "+os.path.basename(fileName),font=LARGE_FONT,bg=HEADER_COLOR,fg='black',bd=2,width=40).grid(columnspan=2,padx=40,pady=10)
        try:
            with open(fileName) as f:
                self.args = json.load(f)
        except Exception as e:
            print(e)
        argToLen = lambda x: len(str(x))
        maxArgNameLength = argToLen(max(self.args.keys(),key=lambda x: argToLen(x)))
        maxArgValueLength = argToLen(max(self.args.values(),key=lambda x: argToLen(x)))
        self.trialDuration = self.args["Rule duration"] +\
                                self.args["Delay duration"] +\
                                self.args["Stimulus duration"] + \
                                self.args["Wrong response flash duration"] + \
                                self.args["Wrong response rest duration"]  
        for i,(argName,value) in enumerate(sorted(self.args.items(),key=lambda item: item[0])):
            lName  = Label(self.argFrame,text=str(argName)+ " :",font='Helvetica 12 bold',bg=BACKGROUND_COLOR).grid(row=i+3,column=0,sticky=tk.E)
            lValue = Label(self.argFrame,text=str(value),bg=BACKGROUND_COLOR).grid(row=i+3,column=1,sticky=tk.W,)
        self.updateTime()
        self.isConfigLoaded = True

    def connect(self):
        try:
            comport = self.comEntry.get()
            baudrate = self.baudrateEntry.get()
            if comport == "" or baudrate == "":
                raise Exception("Please fill in all values")
            baudrate = int(baudrate)
            self.ard = MouseArduino(comport,baudrate)
            self.ard.start()
            self.ardInitFrame.destroy()
            self.ardUpdater.start()
            self.ardControlFrame.grid(row=1,column=0)
            self.isArdConnected=True
        except Exception as e:
            messagebox.showerror("Error","Could not connect to Arduino. Make sure port is correct or other program isn't grabbing the port :"+str(e))
        

    def deliverReward(self,event=None):
        self.ard.deliverReward()
    def sendString(self,event=None):
        self.ard.write(self.sendStringEntry.get())
        self.sendStringEntry.delete(0,'end')

    def updateVariable(self):
        while not self.stopUpdating.is_set():
            if self.ard.newMsg.wait(1):
                while not self.ard.msgQueue.empty():
                    self.ard.newMsg.clear()
                    msg = self.ard.msgQueue.get()
                    print(msg)
                    args = Utilities.parse(msg)
                    arg = args[1].strip()
                    if arg == 'LK':
                        self.lickCount.set(self.lickCount.get() + 1)
                        self.lickLabel.configure(bg=ON_COLOR)
                        if self.isSoundOn.get():
                            Sound.cue(0.05)
                        time.sleep(0.2)
                        self.lickLabel.configure(bg=LICK_OFF_COLOR)
                    elif arg == 'startpump':
                        self.pumpButton.configure(bg=ON_COLOR)
                        self.isPumpOn = True
                    elif arg == 'stoppump':
                        self.pumpButton.configure(bg=OFF_COLOR)
                        self.isPumpOn = False

    def togglePump(self,event=None):
        if self.isPumpOn:
            self.ard.stopPump()
        else:
            self.ard.startPump()

    def updateTime(self,event=None):
        numOfTrials = self.numOfTrialsEntry.get()
        try:
            totalDuration = self.trialDuration * int(numOfTrials)
            tmin = totalDuration // 60
            tsec = totalDuration % 60
            timeStr = "{:.0f} Min {:.0f} Sec".format(tmin,tsec)
        except Exception as e:
            timeStr = ""
            print(e)
        self.estTime.set("Estimated duration: {:>10}".format(timeStr))
        
    def startExperiment(self):
        if not self.isConfigLoaded:
            messagebox.showerror("Error","Please load configuration file")
        elif not self.isArdConnected:
            messagebox.showerror("Error","Please connect Arduino")
        else:
            try:
                sessionName = self.sessionNameEntry.get()
                numOfTrials = self.numOfTrialsEntry.get()
                if sessionName == "" or numOfTrials == "":
                    raise Exception("Please fill in all values")
                numOfTrials = int(numOfTrials)
                self.experiment = Decision(self.ard)
                self.experiment.startExperiment(sessionName,numOfTrials,self.configFileName)
            except Exception as e:
                messagebox.showerror("Error",e)

if __name__ == '__main__':
    try:
        gui = DecisionGui()
        gui.run()
        if gui.ardUpdater.is_alive():
            gui.stopUpdating.set()
        if gui.ard:
            gui.ard.stop()
    except Exception as e:
        print(e)
        input("Press Enter to continue")


