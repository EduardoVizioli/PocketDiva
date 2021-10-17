class Display():
    class BackligtStates():
        k_on = True
        k_off = False

    def drawImage(self,image):
        None
    
    def backlightState(self,state):
        raise NotImplementedError

    def backlightToggle(self,state):
        raise NotImplementedError