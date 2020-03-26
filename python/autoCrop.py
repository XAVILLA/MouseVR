"""
Automatically crop out the black background from our experiment images.
Also make black TRUE black
"""
import cv2
import numpy as np
import sys
import os

def main():
    fileName = sys.argv[1]
    fileNameNoExt = os.path.splitext(os.path.basename(fileName))[0]
    fileExt = os.path.splitext(os.path.basename(fileName))[1]
    filePath = os.path.join(os.getcwd(),fileName)
    fileDir = os.path.dirname(filePath)
    newFileName = "crop_" + fileNameNoExt + fileExt
    newFilePath = os.path.join(fileDir,newFileName)
    img = cv2.imread(filePath,cv2.IMREAD_UNCHANGED)
    gImg = img
    #gImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #gImg = gImg - (gImg<20)*gImg
    left = find(gImg,1,0)
    right = find(gImg,1,1)
    top = find(gImg,0,0)
    bottom = find(gImg,0,1)
    newImg = gImg[top:bottom,left:right]
    cv2.imwrite(newFilePath,newImg)


def find(img,axis,reverse):
    if axis == 0:
        vectorPick = lambda i : img[i,:]
    elif axis == 1:
        vectorPick = lambda i : img[:,i]
    if reverse:
        increment  = lambda i : i-1
    else:
        increment  = lambda i : i+1
    i = 0
    prevVec = vectorPick(i)
    i = increment(i)
    while np.array_equal(vectorPick(i),prevVec):
        prevVec = vectorPick(i)
        i = increment(i)
    return i


if __name__ == "__main__":
    main()
