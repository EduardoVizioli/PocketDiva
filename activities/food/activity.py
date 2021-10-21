from abstract import Activity, Display
from PIL import Image, ImageDraw
from datetime import datetime
from widgets import Battery

class Main(Activity):
    def __init__(self,engine):
        self.battery = Battery(engine)
        self.engine = engine

    def process(self,engine):
        key_pressed = engine.input.getKey()
        if key_pressed == None:
            return

        if key_pressed['key'] == engine.input.Buttons.k_bottom:
            engine.setActivity('main')
            
    def backgroundProcess(self,engine):
        None

    def switch(self,engine):
        engine.setUpdatesPerSecond(1)

    def draw(self):
        image = Image.new("1", (Display.k_width, Display.k_height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0,0,Display.k_width,Display.k_height), outline=255, fill=255)
        
        self.battery.draw(draw,image)

        return image
