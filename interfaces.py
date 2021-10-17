from abstract import Display
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

class PcInput():
    None