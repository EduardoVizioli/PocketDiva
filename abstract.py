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

    def backlightOn(self):
        None

    def backlightOff(self):
        None

    def backlightToggle(self):
        None

#Defines the base characteristics of the input device.
class Input():
    class Buttons():
        k_top = 0
        k_bottom = 1
    
    def getBackgroundBuffer(self):
        background_buffer = self.background_buffer.copy()
        self.background_buffer = []
        return background_buffer

    def readBuffer(self):
        buffer = self.buffer.copy()
        self.buffer = []
        return buffer

    def getKey(self):
        try:
            return self.buffer.pop()
        except IndexError:
            return None


class Battery():
    def getPercentage(self):
        raise NotImplementedError