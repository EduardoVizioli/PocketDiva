class Display():
    k_width = 84
    k_height = 48
    class BackligtStates():
        k_on = True
        k_off = False

    def drawImage(self,image):
        None
    
    def setBacklightState(self,state):
        raise NotImplementedError

    def backlightToggle(self,state):
        raise NotImplementedError