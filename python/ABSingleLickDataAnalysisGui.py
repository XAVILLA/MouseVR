import tkinter as tk
from tkinter import *
from tkinter.ttk import Combobox
import tkinter.messagebox
import csv
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import Utilities
import datetime
import dataAnalysis

LARGE_FONT = ("Verdana", 14)
BACKGROUND_COLOR = '#ced8e1'
BACKGROUND_COLOR_LIGHT = '#dde4eb'
HEADER_COLOR = '#112b3d'
LABEL_COLOR = '#2cc7a0'
TEXT_FONT = 'helvetica 12 bold'
LICK_OFF_COLOR= '#6b6b6b'
LICK_FONT = 'Verdana 40 bold'
ON_COLOR = 'green'
OFF_COLOR = 'red'
STATUS_FONT = 'Verdana 20 bold'

class ABSingleLickGui:
    def __init__(self,master=Tk()):
        self.fileNames = Utilities.findFiles(os.path.join('..','AppleBanana','data'),'csv',False,False)
        setOfMouse = set()
        setOfConfig = set()
        setOfDate = set()
        self.master = master
        self.master.title("Apple/Banana Single Lick Data Analysis")
        self.master.configure(bg=BACKGROUND_COLOR)
        self.titleLabel = Label(self.master,text='AppleBanana Single Lick Experiment Data Analysis',font=STATUS_FONT,bg=BACKGROUND_COLOR)


        #Frames
        
        self.resultFrame = Frame(self.master,bd=3,relief='groove',bg=BACKGROUND_COLOR)
        
        for fName in self.fileNames:
            setOfMouse.add(fName.split('_')[2][:-4])
            fdatetime = fName.split('_')[0]
            fdate = Utilities.strToDate(fdatetime.split('-')[0])
            ftime = Utilities.strToTime(fdatetime.split('-')[1])
            dayStartTime = datetime.time(5,0)
            if ftime < dayStartTime:
                fdate = fdate - datetime.timedelta(days=1)
            setOfDate.add(fdate.strftime('%Y%m%d'))
            setOfConfig.add(fName.split('_')[1])

        listOfMouse = list(setOfMouse)
        listOfMouse.sort()
        #resultFrame
        self.resultStatFrame = Frame(self.resultFrame,bg=BACKGROUND_COLOR)
        self.resultStatFrame.grid(row=0,column=0)

        #configureFrame
        self.configureFrame = Frame(self.master,bd=3,relief='groove',bg=BACKGROUND_COLOR)
        self.configureFrame.grid_columnconfigure(0)
        self.configureFrame.grid_columnconfigure(1,weight=1,uniform='penguin')
        self.configureFrame.grid_columnconfigure(2,weight=1,uniform='penguin')
            #selectMouseFrame
        self.selectMouseFrame = Frame(self.configureFrame,bd=3,relief='groove',bg=BACKGROUND_COLOR)
        self.selectMouseFrameLabel = Label(self.selectMouseFrame,text="Main Config",bg=HEADER_COLOR,font=LARGE_FONT,fg='white',relief='solid',borderwidth=2,width=30)
        self.selectMouseLabel = Label(self.selectMouseFrame,text='Select MouseID :',font=TEXT_FONT,bg=BACKGROUND_COLOR)
        self.selectMouseCombobox = Combobox(self.selectMouseFrame,values=listOfMouse,text='Select Mouse',width=10,state='readonly')
        self.selectMouseCombobox.current(0)
        self.selectSmaLabel = Label(self.selectMouseFrame,text='SMA Average time :',font=TEXT_FONT,bg=BACKGROUND_COLOR)
        self.selectSmaEntry = Entry(self.selectMouseFrame)
        self.analyzeButton = Button(self.selectMouseFrame,width=16,text='Kowalsky Analysis',height=2,font=STATUS_FONT,command=self.analyze)
        self.selectMouseFrameLabel.grid(row=0,column=0,columnspan=2)
        self.selectMouseLabel.grid(row=1,column=0,pady=20,padx=3)
        self.selectMouseCombobox.grid(row=1,column=1,pady=20,padx=3,sticky='NWES')
        self.selectSmaLabel.grid(row=2,column=0,pady=20,padx=3,sticky='NWES')
        self.selectSmaEntry.grid(row=2,column=1,pady=20,padx=3,sticky='NWES')
        self.analyzeButton.grid(row=3,column=0,columnspan=2,pady=15,sticky='NWES')


            #selectConfigFrame
        self.selectConfigFrame = Frame(self.configureFrame,bd=3,relief='groove',bg=BACKGROUND_COLOR)
        self.selectConfigFrameLabel = Label(self.selectConfigFrame,text="Select Configuration",bg=HEADER_COLOR,font=LARGE_FONT,fg='white',relief='solid',borderwidth=2,width=30)
        self.selectConfigMultipleFrame = selectMultipleFrame(self.selectConfigFrame,'Config',setOfConfig)
        self.selectConfigFrameLabel.pack()
        self.selectConfigMultipleFrame.pack(padx=10,pady=10)
        self.selectConfigMultipleFrame.pack()
            #selectDateFrame
        self.selectDateFrame = Frame(self.configureFrame,bd=3,relief='groove',bg=BACKGROUND_COLOR)
        self.selectDateFrameLabel = Label(self.selectDateFrame,text="Select Date",bg=HEADER_COLOR,font=LARGE_FONT,fg='white',relief='solid',borderwidth=2,width=35)
        self.selectDateMultipleFrame = selectMultipleFrame(self.selectDateFrame,'Date',setOfDate)
        self.selectDateDisclaimer = Label(self.selectDateFrame,text='Day starts at 5AM',bg=BACKGROUND_COLOR)
        self.selectDateDisclaimer2 = Label(self.selectDateFrame,text='Jan 2nd 3:00 AM will be considered Jan 1st',bg=BACKGROUND_COLOR)
        self.selectDateFrameLabel.pack()
        self.selectDateMultipleFrame.pack(padx=10,pady=10)
        self.selectDateDisclaimer.pack()
        self.selectDateDisclaimer2.pack()
            #Grid Config for configure Frame
        self.selectMouseFrame.grid(row=0,column=0,sticky='NWES')
        self.selectConfigFrame.grid(row=0,column=1,sticky='NWES')
        self.selectDateFrame.grid(row=0,column=2,sticky='NWES')
        
        self.configureFrame.grid(sticky='NWES')
        self.resultFrame.grid(sticky='NWES')
        
    def run(self):
        self.master.mainloop()

    def updateConfigAvailable(self):
        raise NotImplemented()
    def updateDateAvailable(self):
        raise NotImplemented()
        
    def analyze(self,event=None):
        mouse = self.selectMouseCombobox.get()
        configlist = self.selectConfigMultipleFrame.curselection()
        datelist = self.selectDateMultipleFrame.curselection()
        smaAvgBy = self.selectSmaEntry.get()
        resultfNames = []
        if not mouse:
            tkinter.messagebox.showerror("hey","Please Select Mouse")
            return
        elif not configlist:
            tkinter.messagebox.showerror("hey","Please Select config file")
            return
        elif not datelist:
            tkinter.messagebox.showerror("hey","Please Select Date")
            return
        elif not smaAvgBy:
            tkinter.messagebox.showerror("hey","Please enter SMA Average time")
            return
        try:
            smaAvgBy = int(smaAvgBy)
        except:
            tkinter.messagebox.showerror("hey","Please enter valid SMA Average time number")
            return
        for fName in self.fileNames:
            fmouse = fName.split('_')[2][:-4]
            fconfig = fName.split('_')[1]
            fdatetime = fName.split('_')[0]
            fdate = Utilities.strToDate(fdatetime.split('-')[0])
            ftime = Utilities.strToTime(fdatetime.split('-')[1])
            dayStartTime = datetime.time(5,0)
            if ftime < dayStartTime:
                fdate = fdate - datetime.timedelta(days=1)
            if fmouse in [mouse]  and fconfig in configlist and fdate.strftime("%Y%m%d") in datelist:
                resultfNames.append(fName)
        result = dataAnalysis.smaAnalyze(resultfNames,smaAvgBy)
        fig = plt.figure(figsize=(5.5,2),dpi=100)
        plt.rcParams.update({'font.size': 3})
        ax = plt.subplot(2,1,1)
        xaxis = list(range(len(result['precision'])))
        for i in range(len(xaxis)):
            xaxis[i] += smaAvgBy
        ax.plot(xaxis,result['precision'],label='Precision',linewidth=0.4)
        ax.plot(xaxis,result['recall'],label='Recall',linewidth=0.4)
        #ax.set_title(240770)
        ax.set(ylim=(0,1))
        ax.legend(['Precision','Recall'],prop={'size':3},loc='upper left')
        for index,date in result['dateline']:
            ax.vlines(index,0,1,colors='grey',label=date.strftime("%Y%m%d"),linewidth=0.3)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(100))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(10))
        ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.0%}'))
        ax.yaxis.tick_right()
        ax.tick_params(axis="y",direction="in", pad=-12)
        ax.tick_params(axis="x",direction="in", pad=-8)
        self.mouseLabel = Label(self.resultStatFrame,text="MouseID:{}".format(mouse),bg=BACKGROUND_COLOR)
        self.tpLabel = Label(self.resultStatFrame,text="tp:{}".format(result['tp']),bg=BACKGROUND_COLOR)
        self.tnLabel = Label(self.resultStatFrame,text="tn:{}".format(result['tn']),bg=BACKGROUND_COLOR)
        self.fpLabel = Label(self.resultStatFrame,text="fp:{}".format(result['fp']),bg=BACKGROUND_COLOR)
        self.fnLabel = Label(self.resultStatFrame,text="fn:{}".format(result['fn']),bg=BACKGROUND_COLOR)
        self.precisionLabel = Label(self.resultStatFrame,text="Final Precision: {:.2%}".format(result['precision'][-1]),bg=BACKGROUND_COLOR)
        self.recallLabel = Label(self.resultStatFrame,text="Final Recall: {:.2%}".format(result['recall'][-1]),bg=BACKGROUND_COLOR)
        imgCount = len(result['imageAccuracy'])
        for i,img in enumerate(sorted(result['imageAccuracy'].keys())):
                ax = plt.subplot(2,imgCount,imgCount+i+1)
                ax.plot(result['imageAccuracy'][img],linewidth=0.4)
                ax.set_title(img,x=0.2,y=0.8,fontsize=3)
                ax.set(ylim=(0,1))
                ax.yaxis.tick_right()
                ax.xaxis.set_major_locator(ticker.MultipleLocator(200))
                ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.0%}'))
                ax.tick_params(axis="y",direction="in", pad=-12)
                ax.tick_params(axis="x",direction="in", pad=-8)
                for tick in ax.xaxis.get_major_ticks():
                    tick.label.set_fontsize(3)
        fig.tight_layout()
        pltCanvas = FigureCanvasTkAgg(fig, self.resultFrame)
        pltCanvas.get_tk_widget().grid(row=0,column=1,sticky='WE')

        self.mouseLabel.grid(row=0,column=0,sticky='NW')
        self.tpLabel.grid(row=1,column=0,sticky='NW')
        self.tnLabel.grid(row=2,column=0,sticky='NW')
        self.fpLabel.grid(row=3,column=0,sticky='NW')
        self.fnLabel.grid(row=4,column=0,sticky='NW')
        self.precisionLabel.grid(row=5,column=0,sticky='NW')
        self.recallLabel.grid(row=6,column=0,sticky='NW')
        
        


class selectMultipleFrame(tk.Frame):
    def __init__(self,master,title,items):
        tk.Frame.__init__(self,master,bg=BACKGROUND_COLOR)
        self.title = Label(self,text=title,font=TEXT_FONT,bg=BACKGROUND_COLOR)
        self.availableListFrame = Frame(self,bg=BACKGROUND_COLOR)
        self.availableListboxScrollbar = Scrollbar(self.availableListFrame, orient="vertical")
        self.availableListbox = Listbox(self.availableListFrame,selectmode=EXTENDED,yscrollcommand=self.availableListboxScrollbar.set)
        self.availableListboxScrollbar.config(command=self.availableListbox.yview)
        self.selectedListFrame = Frame(self,bg=BACKGROUND_COLOR)
        self.selectedListboxScrollbar = Scrollbar(self.selectedListFrame, orient="vertical")
        self.selectedListbox = Listbox(self.selectedListFrame,selectmode=EXTENDED,yscrollcommand=self.selectedListboxScrollbar.set)
        self.selectedListboxScrollbar.config(command=self.selectedListbox.yview)
        self.availableListbox.pack(side='left',fill='y')
        self.selectedListbox.pack(side='left',fill='y')
        self.availableListboxScrollbar.pack(side='right',fill='y')
        self.selectedListboxScrollbar.pack(side='right',fill='y')
        self.addButton = Button(self,text='>>>',command=self.addEntries,bg=BACKGROUND_COLOR)
        self.removeButton = Button(self,text='<<<',command=self.removeEntries,bg=BACKGROUND_COLOR)
        self.availableLabel = Label(self,text='Available',font=TEXT_FONT,bg=BACKGROUND_COLOR)
        self.selectedLabel = Label(self,text='Selected',font=TEXT_FONT,bg=BACKGROUND_COLOR)
        items = list(items)
        items.sort()
        for i in items:
            self.availableListbox.insert(END,i)
        self.availableLabel.grid(row=0,column=0)
        self.selectedLabel.grid(row=0,column=2)
        self.availableListFrame.grid(row=1,column=0,rowspan=2)
        self.addButton.grid(row=1,column=1)
        self.removeButton.grid(row=2,column=1)
        self.selectedListFrame.grid(row=1,column=2,rowspan=2)
        self.availableListbox.bind("<Double-Button-1>", self.addEntry)
        self.selectedListbox.bind("<Double-Button-1>", self.removeEntry)
        
    def addEntries(self):
        items = self.availableListbox.curselection()
        for i in items[::-1]:
            value = self.availableListbox.get(i)
            self.availableListbox.delete(i)
            index = 0
            self.sortedInsert(value,self.selectedListbox)
        
    def removeEntries(self):
        items = self.selectedListbox.curselection()
        for i in items[::-1]:
            value = self.selectedListbox.get(i)
            self.selectedListbox.delete(i)
            index = 0
            self.sortedInsert(value,self.availableListbox)
            
    def addEntry(self,item):
            value = self.availableListbox.get(ACTIVE)
            if value:
                self.sortedInsert(value,self.selectedListbox)
                self.availableListbox.delete(ACTIVE)
    def removeEntry(self,item):
            value = self.selectedListbox.get(ACTIVE)
            if value:
                self.sortedInsert(value,self.availableListbox)
                self.selectedListbox.delete(ACTIVE)
        
        
    @staticmethod
    def sortedInsert(value,lst):
        index = 0
        while index < lst.size():
                if value > lst.get(index):
                    index += 1
                else:
                    break
        lst.insert(index,value)
        
        
        
    def curselection(self):
        return self.selectedListbox.get(0,last=self.selectedListbox.size())


if __name__ == '__main__':
    gui = ABSingleLickGui()
    gui.run()
