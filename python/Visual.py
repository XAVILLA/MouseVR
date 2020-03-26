import pygame
import sys
import threading
import time
import math

class Visual(threading.Thread):
    BLACK = (0,0,0)
    GREEN = (0,255,0)
    RED   = (255,0,0)
    WHITE = (255,255,255)
    ORANGE = (255,165,0)
    GREY = (51,51,51)
    """
    imageNames - full path image file names
    monitorSize - monitor diagonal length in inches
    distance - distance from mouse's eye to the monitor
    """
    def __init__(self,imageNames,monitorSize,distance,isFullScreen=True):
        threading.Thread.__init__(self)
        self.imageNames = imageNames
        self.images = {}
        self.currentImageIdx = None
        self.currentImageDegree = 1
        self.fullColor = self.GREY
        self.borderColor = self.GREEN
        self.bottomLineColor = self.WHITE
        self.fillFullColor = False
        self.fillBorderColor = False
        self.fillBottomLineColor = False
        self.flash = False
        self.flashColorA = self.BLACK
        self.flashColorB = self.WHITE
        self.showImage = False
        self.imported = False
        self.timeout = 0
        self.flashTimeout = 0
        self.finished = False
        self.isFullScreen = isFullScreen
        self.distance = distance #Monitor distance in centimeters
        self.monitorSize = monitorSize * 2.54 # Convert inch to cm
        

    def run(self):
        pygame.init()
        if self.isFullScreen:
            screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((1024,800)) #Windowed Mode
        pygame.mouse.set_visible(False)
        w,h = pygame.display.get_surface().get_size()
        vertPixelsPerCm = h/(math.sin(math.atan(h/w))*self.monitorSize)
        screen_rect = screen.get_rect()
        self.loadImages()
        while True: 
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: 
                    self.finished = True
                    pygame.display.quit()
                    pygame.quit()
                    return
            screen.fill(self.GREY)
            if self.fillFullColor and not self.flash:
                if pygame.time.get_ticks() < self.timeout:
                    screen.fill(self.fullColor)
                else:
                    self.fillFullColor = False
            elif self.showImage:
                if pygame.time.get_ticks() < self.timeout:
                    img = self.images[self.currentImage]
                    oldW,oldH = img.get_rect().size[0],img.get_rect().size[1]
                    newH = round(2*self.scaleByDegree(self.currentImageDegree/2)*vertPixelsPerCm)
                    newW = round(newH/oldH*oldW)
                    newImg = pygame.transform.scale(img,(newW,newH))
                    rect = newImg.get_rect()
                    rect.center = (round(self.coord[0]*w),round(self.coord[1]*h))
                    screen.blit(newImg,rect)
                else:
                    self.showImage = False
            elif self.flash:
                if pygame.time.get_ticks() < self.flashTimeout:
                    if round(time.time()*1000/self.tFlashGap)%2 == 1:
                        screen.fill(self.flashColorA)
                    else:
                        screen.fill(self.flashColorB)
                else:
                    self.flash = False
            if self.fillBorderColor and pygame.time.get_ticks() < self.timeout:
                pygame.draw.rect(screen,self.borderColor,screen_rect)
            if self.fillBottomLineColor and pygame.time.get_ticks() < self.timeout:
                pygame.draw.line(screen,self.bottomLineColor,(0,h),(w,h),width=round(w/10))
            pygame.display.flip()

    def loadImages(self):
        self.checkAlive()
        self.images = {}
        for imgName in self.imageNames:
            try:
                img = pygame.image.load(imgName)
                img.convert()
                if imgName in self.images:
                    raise ValueError("{} file imported twice".format(imgName))
                self.images[imgName] = img
            except pygame.error as msg:
                print("Could not import image, ",imgName,msg)
                self.close()

    def cue(self):
        self.checkAlive()
        self.cancelAll()

        
    def drawText(self,text,font,centerW,centerH,screen):
        self.checkAlive()
        centerW,centerH = round(centerW),round(centerH)
        surf = font.render(text,True,self.BLACK)
        rect = surf.get_rect()
        rect.center = (centerW,centerH)
        screen.blit(surf,rect)

    def correct(self,timeout):
        self.checkAlive()
        self.timeout = pygame.time.get_ticks() + timeout*1000
        
    def wrong(self,flashTimeout,restTimeout,tFlashGap=100):
        self.checkAlive()
        self.cancelAll()
        self.tFlashGap = tFlashGap
        self.fullColor = self.BLACK
        t = pygame.time.get_ticks()
        self.flashTimeout = t + flashTimeout*1000
        self.timeout = self.flashTimeout+restTimeout*1000
        self.flash=True
        self.fillFullColor = True

    def lick(self,screen,w,h,timeout):
        self.checkAlive()
        pygame.draw.line(screen,self.bottomLineColor,(0,h),(w,h),width=round(w/10))
        self.fillBottomLineColor = True

    def show(self,imgName,degree,coord,timeout):
        self.checkAlive()
        self.cancelAll()
        self.currentImage = imgName
        self.showImage = True
        self.currentImageDegree = degree
        self.coord = coord
        self.timeout = pygame.time.get_ticks() + timeout*1000

    def close(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))


    def cancelAll(self):
        self.checkAlive()
        self.showImage = False
        self.flash = False
        self.fillFullColor = False
        self.fillBorderColor = False
        self.fillBottomLineColor = False

    def checkAlive(self):
        try:
            if self.finished:
                raise Exception
            pygame.display.Info()
        except Exception as e:
            print(e)
            raise Exception("The display has quit already")
            
        

    """
    Return the length of the image
    """
    def scaleByDegree(self,degree):
        return math.tan(2*degree*math.pi/180)*self.distance


        


