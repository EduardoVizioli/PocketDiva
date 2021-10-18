class Activity(object):
    def process(self,engine):
        None

    def draw(self):
        return None

    def backgroundProcess(self,engine):
        None

class Display():
    k_width = 84
    k_height = 48
    class BacklightStates():
        k_on = True
        k_off = False

    def drawImage(self,image):
        None
    
    def setBacklightState(self,state):
        raise NotImplementedError

    def backlightToggle(self,state):
        raise NotImplementedError

class Input():
    class Buttons():
        k_left = 0
        k_center = 1
        k_right = 2
    
    def readBuffer(self):
        raise NotImplementedError