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

    class Dock():
        def __init__(self):
            self.selected_action = 0
            self.dock_actions_cnt = 5
            self.dock_height = 10
        
        def next(self):
            if self.selected_action < self.dock_actions_cnt - 1:
                self.selected_action = self.selected_action + 1
        
        def previous(self):
            if self.selected_action > 0:
                self.selected_action = self.selected_action - 1

        def select(self):
            print("selected:"+str(self.selected_action))
        
        def draw(self,draw,image):
            
            #draw.rectangle((0,48,42,38),outline=0,fill=255)
            for i in range(0,self.dock_actions_cnt):
                icon_width = (Display.k_width/self.dock_actions_cnt)
                left_start = i*icon_width
                left_end = left_start+icon_width
                bottom_start = Display.k_height-1
                bottom_end = Display.k_height-self.dock_height
                fill = 255
                if i == self.selected_action:
                    fill = 0

                draw.rectangle((left_start,bottom_start,left_end,bottom_end),outline=0,fill=fill)
                

    def __init__(self):
        self.statusBar = self.StatusBar()
        self.dock = self.Dock()

    def process(self,engine):
        key_pressed = engine.input.getKey()
        if key_pressed == None:
            return

        if key_pressed == Input.Buttons.k_left:
            self.dock.previous()
        elif key_pressed == Input.Buttons.k_center:
            self.dock.select()
        elif key_pressed == Input.Buttons.k_right:
            self.dock.next()

    def draw(self):
        image = Image.new("1", (Display.k_width, Display.k_height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0,0,Display.k_width,Display.k_height), outline=255, fill=255)
        
        self.statusBar.draw(draw,image)
        self.dock.draw(draw,image)

        return image

