#Defines how an activity should look like
class Activity(object):
    def __init__(self,engine):
        None
    
    def process(self,engine):
        None

    def draw(self):
        return None

    def backgroundProcess(self,engine):
        None
    
    def switch(self,engine):
        None

#Defines the base characteristics of the display.
class Display():
    k_width = 84
    k_height = 48
    k_rowpixels = k_height//6
    def drawImage(self,image):
        None

#Defines the base characteristics of the input device.
class Input():
    class Buttons():
        k_top = 0
        k_bottom = 1
    
    def readBuffer(self):
        raise NotImplementedError
    
    def getKey(self):
        raise NotImplementedError


class Battery():
    def getPercentage(self):
        raise NotImplementedError