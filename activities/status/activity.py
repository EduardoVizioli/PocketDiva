from abstract import Activity, Display
from widgets import Battery, Clock
from PIL import Image, ImageDraw
from graphics import TextDraw
from utils import Utils

class Main(Activity):
    class StatusConstants():
        k_status_spacement = 9

    def __init__(self,engine):
        self.engine = engine
        self.battery = Battery(engine)
        self.clock = Clock()
        self.miku_status = {}

    def process(self,engine):
        miku = engine.getActivity('main').miku
        self.miku_status = miku.getStatus()
        self.miku_max_status = miku.MikuConstants.k_maximum_status
        
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
        image = Image.new('1', (Display.k_width, Display.k_height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0,0,Display.k_width,Display.k_height), outline=255, fill=255)

        self.battery.draw(draw,image)
        self.clock.draw(draw,image)

        self.spacement = self.StatusConstants.k_status_spacement
        for status_name in self.miku_status:
            TextDraw.text(image,status_name+'@'+str(Utils.percent_from_value(self.miku_status[status_name],self.miku_max_status[status_name])),1,self.spacement)
            self.spacement = self.spacement + self.StatusConstants.k_status_spacement

        return image

