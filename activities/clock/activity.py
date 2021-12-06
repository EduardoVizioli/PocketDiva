from abstract import Activity
from graphics import TextDraw
from datetime import datetime
from widgets import Battery

class Main(Activity):
    class Clock():
        def __init__(self):
            self.text_draw = TextDraw()

        def draw(self,draw,image):
            now = datetime.now()
            self.text_draw.text(image,now.strftime("%H@%M"),6,18,scale=3)

    def __init__(self,engine):
        self.clock = self.Clock()
        self.battery = Battery(engine)
        self.engine = engine

    def process(self,engine):
        key_pressed = engine.input.getKey()
        if key_pressed == None:
            return

        if key_pressed['key'] == engine.input.Buttons.k_bottom:
            engine.setActivity('main')

    def switch(self,engine):
        engine.setUpdatesPerSecond(1)

    def draw(self,draw,image):
        self.clock.draw(draw,image)
        self.battery.draw(draw,image)
        return image

