import random
import numpy as np
import os
import datetime

"""Return index according to the probability
Args:
    weightsList (list) : probability distribution ex) [1,1,2] Doesn't have to be normalized
Returns:
    idx: Randomly chosen integer according to the probability
"""
def pickByWeight(weightsList):
    w = np.array(weightsList)/np.sum(weightsList)
    idx = np.random.choice(range(len(weightsList)),p=w)
    return idx

"""
Retun random item from list
"""
def choice(lst):
    return np.random.choice(lst)
        
"""
Split string into list of strings delimited with comma
"""
def parse(string):
    return string.split(',')

"""
Return list of all files in the folderName.
acceptedExtension is a filter that'll return files with only the list of extension specified ex) [".jpg",".png"]
if returnFullPath is true, it will return full path name for all images. By default it returns relative path
"""
def findFiles(folderName,acceptedExtension=None,returnFullPath = True,includeHidden = False):
    fileNames = []
    if not os.path.exists(folderName):
        raise ValueError("Folder {} doesn't exist".format(folderName))
    for root,_,files in os.walk(folderName):
        for f in files:
            if acceptedExtension == None or any([ext == f[-(len(ext)):] for ext in acceptedExtension]):
                if not includeHidden and f[0] == '.':
                    continue
                if returnFullPath:
                    fileNames.append(os.path.join(root,f))
                else:
                    fileNames.append(os.path.relpath(os.path.join(root,f),folderName))
    return fileNames
        
"""
Check if 'var' has the instance type of 'instanceType'
You can also pass in custom filter for 'var'
"""
def checkInput(var,instanceType,customFilter=lambda x: True):
    if not customFilter(var):
        raise ValueError("JSON argument {} does not satisfy requirement".format(var))
    elif isinstance(instanceType,list):
        if not var in instanceType:
            raise ValueError("JSON argument {} is not in {}".format(var,instanceType))
    elif not isinstance(var,instanceType):
        raise ValueError("JSON argument {} is not {}".format(var,instanceType))

"""
Convert datetime format we use in naming ABSingleLick experiments to datetime object
"""
def strToDatetime(strDatetime):
    rawDate = strDatetime.split('-')[0]
    rawTime = strDatetime.split('-')[1]
    result = datetime.datetime.combine(strToDate(rawDate),strToTime(rawTime))
    return result
    
"""
Convert date format we use in naming ABSingleLick experiments to datetime object
"""
def strToDate(strDate):
    f = lambda x: int(x.lstrip('0'))
    result = datetime.date(f(strDate[:4]),f(strDate[4:6]),f(strDate[6:8]))
    return result
"""
Convert time format we use in naming ABSingleLick experiments to datetime object
"""
def strToTime(strTime):
    f = lambda x:  int(x[1]) if x[0] == '0' else int(x)
    result = datetime.time(f(strTime[:2]),f(strTime[2:4]))
    return result
