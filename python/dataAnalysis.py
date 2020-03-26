import os
import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import datetime
import Utilities
import numpy as np
import pickle


def smaAnalyze(fileNames,avgBy):
    fileNames.sort()
    trials = 0
    lastDate = None
    result = {}
    imageAccuracy = []
    count = []
    tp = []
    tn = []
    fp = []
    fn = []
    precision = []
    recall = []
    dateline = []
    imageAccuracy = {}
    for fName in fileNames:
        fdatetime = fName.split('_')[0]
        fdate = Utilities.strToDate(fdatetime.split('-')[0])
        ftime = Utilities.strToTime(fdatetime.split('-')[1])
        dayStartTime = datetime.time(5,0)
        if ftime < dayStartTime:
            fdate = fdate - datetime.timedelta(days=1)
        if trials == 0:
            lastDate = fdate
        if fdate != lastDate:
            dateline.append((trials,datetime.datetime.combine(fdate,dayStartTime)))
            lastDate = fdate
        f = open(os.path.join('..','AppleBanana','data',fName))
        reader = csv.reader(f,delimiter=',',quoting=csv.QUOTE_MINIMAL)
        #(tp,tn,fp,fn)
        trialCount = 0
        for t in reader:
            imgName = t[0]
            isAimg = t[1]
            lickTime = t[2]
            acc = imageAccuracy
            if imgName not in acc:
                acc[imgName] = []
            istp = False
            isfn = False
            isfp = False
            istn = False
            isCorrect = None
            if int(isAimg) == 1:
                if float(lickTime) > 0:
                    istp = True
                    isCorrect = True
                else:
                    isfn = True
                    isCorrect = False
            else:
                if float(lickTime) > 0:
                    isfp = True
                    isCorrect = False
                else:
                    istn = True
                    isCorrect = True
            tp.append(istp + (tp[-1] if len(tp) else 0))
            fn.append(isfn + (fn[-1] if len(fn) else 0))
            fp.append(isfp + (fp[-1] if len(fp) else 0))
            tn.append(istn + (tn[-1] if len(tn) else 0))
            acc[imgName].append(isCorrect+(acc[imgName][-1] if len(acc[imgName]) else 0))
            trials += 1
    movingtp = np.array(tp[avgBy-1:]) - np.array([0] + tp[:-avgBy])
    movingfp = np.array(fp[avgBy-1:]) - np.array([0] + fp[:-avgBy])
    movingfn = np.array(fn[avgBy-1:]) - np.array([0] + fn[:-avgBy])
    movingtn = np.array(tn[avgBy-1:]) - np.array([0] + tn[:-avgBy])
    movingacc = {}
    acc = imageAccuracy
    for img in acc:
        movingimg = np.array(acc[img])[avgBy-1:] - np.array([0] + acc[img])[:-avgBy]
        movingimg = movingimg / avgBy
        movingacc[img] = movingimg
    denom = movingtp+movingfp
    precision = movingtp/(denom)
    precision[np.where(denom==0)] = 0
    denom = movingtp+movingfn
    recall = movingtp/(denom)
    recall[np.where(denom==0)] = 0
    result['precision'] = precision
    result['recall'] = recall
    result['imageAccuracy'] = movingacc
    result['dateline'] = dateline
    result['tp'] = tp[-1]
    result['fp'] = fp[-1]
    result['fn'] = fn[-1]
    result['tn'] = tn[-1]
    return result

def testsmaAnalyze():
    testFile = ['20191203-0018_phase1_240770.csv','20191203-2011_phase1_240770.csv']
    actual = smaAnalyze(testFile,20)
    expected = importResult('smaAnalyzeTest.P')
    assert(all(expected['precision'] == actual['precision']))
    assert(all(expected['recall'] == actual['recall']))
    assert(len(expected['imageAccuracy']) == len(expected['imageAccuracy']))
    for key in expected['imageAccuracy']:
        assert(all(expected['imageAccuracy'][key] == actual['imageAccuracy'][key]))
    assert(expected['dateline'] == actual['dateline'])
    assert(expected['tp'] == actual['tp'])
    assert(expected['fp'] == actual['fp'])
    assert(expected['fn'] == actual['fn'])
    assert(expected['tn'] == actual['tn'])
    print('SMA Analyze Test all PASSED')

def exportResult(result,filepath):
    f = open(filepath,'wb+')
    pickle.dump(result,f)
    f.close()
    
def importResult(filepath):
    f = open(filepath,'rb')
    result = pickle.load(f)
    f.close()
    return result
    



if __name__ == '__main__':
    fileNames = Utilities.findFiles(os.path.join('..','AppleBanana','data'),'csv',False,False)
    avgBy = 20
    result =  smaAnalyze(fileNames,avgBy)
    fig = plt.figure()
    ax = plt.subplot(2,1,1)
    xaxis = np.array(range(0,len(result['precision']))) + avgBy
    ax.plot(xaxis,result['precision'],label='Precision')
    ax.plot(xaxis,result['recall'],label='Recall')
    ax.set_title(240770)
    ax.set(ylim=(0,1))
    ax.legend(['Precision','Recall'])
    for index,date in result['dateline']:
        ax.vlines(index,0,1,colors='grey',label=date)
        ax.legend(prop={'size': 4})
    ax.xaxis.set_major_locator(ticker.MultipleLocator(100))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(10))
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.0%}'))
    print("tp:{},tn:{},fp:{},fn:{}".format(result['tp'],result['tn'],result['fp'],result['fn']))
    print("Final Precision : {:.2%}".format(result['precision'][-1]))
    print("Final Recall : {:.2%}".format(result['recall'][-1]))
    imgCount = len(result['imageAccuracy'])
    for i,img in enumerate(sorted(result['imageAccuracy'].keys())):
            ax = plt.subplot(2,imgCount,imgCount+i+1)
            ax.plot(result['imageAccuracy'][img])
            ax.set_title(img)
            ax.set(ylim=(0,1))
            ax.xaxis.set_major_locator(ticker.MultipleLocator(200))
            ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.0%}'))
            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(5)
    fig.tight_layout()
    fig.show()
    plt.show()
