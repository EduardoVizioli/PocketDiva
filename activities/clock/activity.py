from abstract import Activity, Display
from PIL import Image, ImageDraw
from graphics import TextDraw
from datetime import datetime

class Main(Activity):
    class Clock():
        def __init__(self):
            None

        def draw(self,draw,image):
            now = datetime.now()
            TextDraw.text(image,now.strftime("%H@%M"),6,16,scale=3)

    def __init__(self):
        self.clock = self.Clock()

    def process(self,engine):
        key_pressed = engine.input.getKey()
        if key_pressed == None:
            return

        if key_pressed['key'] == engine.input.Buttons.k_bottom:
            engine.setActivity('main')
            

    def backgroundProcess(self,engine):
        None

    def draw(self):
        image = Image.new("1", (Display.k_width, Display.k_height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0,0,Display.k_width,Display.k_height), outline=255, fill=255)
        
        self.clock.draw(draw,image)

        return image

