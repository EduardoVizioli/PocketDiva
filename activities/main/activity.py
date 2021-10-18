from abstract import Activity, Display, Input
from PIL import Image, ImageDraw
from graphics import TextDraw
from datetime import datetime

class Main(Activity):
    class StatusBar():
        class Clock():
            def __init__(self):
                None
            def draw(self,draw,image):
                now = datetime.now()
                TextDraw.text(image,now.strftime("%H@%M"),1,1)

        def __init__(self):
            self.line = (0,7,84,7)
            self.clock = self.Clock()
        
        def draw(self,draw,image):
            draw.line(self.line, fill=0)
            self.clock.draw(draw,image)

    def __init__(self):
        self.statusBar = self.StatusBar()

    def process(self,engine):
        key_pressed = engine.input.getKey()
        if key_pressed == Input.Buttons.k_left:
            None
        elif key_pressed == Input.Buttons.k_center:
            None
        elif key_pressed == Input.Buttons.k_right:
            None

    def draw(self):
        image = Image.new("1", (Display.k_width, Display.k_height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0,0,Display.k_width,Display.k_height), outline=255, fill=255)
        
        self.statusBar.draw(draw,image)

        return image

