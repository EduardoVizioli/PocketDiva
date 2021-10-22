from abstract import Activity
from widgets import Battery, Clock
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
        self.text_draw = TextDraw()

    def process(self,engine):
        miku = engine.getActivity('main').miku
        self.miku_status = miku.getStatus()
        self.miku_max_status = miku.MikuConstants.k_maximum_status
        
        key_pressed = engine.input.getKey()
        if key_pressed == None:
            return

        if key_pressed['key'] == engine.input.Buttons.k_bottom:
            engine.setActivity('main')

    def switch(self,engine):
        engine.setUpdatesPerSecond(1)

    def draw(self,draw,image):
        self.battery.draw(draw,image)
        self.clock.draw(draw,image)

        self.spacement = self.StatusConstants.k_status_spacement
        for status_name in self.miku_status:
            self.text_draw.text(image,status_name+'@'+str(Utils.percent_from_value(self.miku_status[status_name],self.miku_max_status[status_name])),1,self.spacement)
            self.spacement = self.spacement + self.StatusConstants.k_status_spacement

        return image

