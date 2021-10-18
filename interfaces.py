from abstract import Display, Input
import numpy
import cv2

k_resize_factor = 4

class PcDisplay(Display):
    def __init__(self):
        None

    def drawImage(self,image):
        image = image.resize((Display.k_width*k_resize_factor,Display.k_height*k_resize_factor))
        array = numpy.float32(image) 
        cv_image = cv2.cvtColor(array, cv2.CV_8UC1)
        cv2.imshow("Pocket Diva", cv_image)
        key = cv2.waitKey(1)
        if cv2.getWindowProperty('Pocket Diva', 0) == -1:
            raise KeyboardInterrupt

class PcInput(Input):
    def __init__(self):
        from pynput.keyboard import Key, Listener
        self.listener = Listener(on_press=self.key_press) 
        self.listener.start()
        self.buffer = []
        self.key = Key

    def key_press(self,key):
        if key == self.key.left and self.Buttons.k_left not in self.buffer:
            self.buffer.append(self.Buttons.k_left)
        elif key == self.key.down and self.Buttons.k_center not in self.buffer:
            self.buffer.append(self.Buttons.k_center)
        elif key == self.key.right and self.Buttons.k_right not in self.buffer:
            self.buffer.append(self.Buttons.k_right)

    def readBuffer(self):
        buffer = self.buffer.copy()
        self.buffer = []
        return buffer
    
    def getKey(self):
        try:
            return self.buffer.pop()
        except IndexError:
            return None