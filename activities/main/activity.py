from abstract import Activity, Display
from PIL import Image, ImageDraw, ImageOps
from graphics import TextDraw
from datetime import datetime
import random
import json
import os

class Main(Activity):
    class StatusBar():
        class Clock():
            def __init__(self):
                None

            def draw(self,draw,image):
                now = datetime.now()
                TextDraw.text(image,now.strftime("%H@%M"),1,1)

        class Battery():
            def __init__(self,engine):
                self.engine = engine

            def draw(self,draw,image):
                percentage = self.engine.battery.getPercentage()
                TextDraw.text(image,percentage,68,1)

        def __init__(self,engine):
            self.line = (0,7,84,7)
            self.clock = self.Clock()
            self.battery = self.Battery(engine)
            self.engine = engine
        
        def draw(self,draw,image):
            draw.line(self.line, fill=0)
            self.clock.draw(draw,image)
            self.battery.draw(draw,image)

    class Dock():
        def __init__(self):
            self.selected_action = 0
            self.dock_height = 10
            with open('./data/dock.json') as json_file:
                self.data = json.load(json_file)
            
            self.dock_actions_cnt = len(self.data['apps'])
            print(self.dock_actions_cnt)

        def next(self):
            if self.selected_action < self.dock_actions_cnt - 1:
                self.selected_action = self.selected_action + 1
            else:
                self.selected_action = 0

        def select(self,engine):
            try:
                engine.setActivity(self.data['apps'][self.selected_action])
            except engine.EngineExceptions.ActivityNotFound:
                None
        
        def draw(self,draw,image):
            for i in range(0,self.dock_actions_cnt):
                icon_width = (Display.k_width/self.dock_actions_cnt)
                left_start = i*icon_width
                left_end = left_start+icon_width
                bottom_start = Display.k_height-1
                bottom_end = Display.k_height-self.dock_height
                try:
                    activity_icon = Image.open('./activities/'+self.data['apps'][i]+'/icon.bmp')
                except FileNotFoundError:
                    activity_icon = None

                fill = 255
                if i == self.selected_action:
                    fill = 0
                    if activity_icon:
                        activity_icon = ImageOps.invert(activity_icon)
                
                if i == self.dock_actions_cnt-1:
                    left_end = left_end - 1
                
                draw.rectangle((left_start,bottom_start,left_end,bottom_end),outline=0,fill=fill)
                
                if activity_icon:
                    image.paste(activity_icon,(int(left_start)+2,int(bottom_end)+1))

    class Miku():
        class MikuProperties():
            k_textures_folder = './textures/miku'
            k_start_position = [15,15]
            k_walking_prob = 15
        def __init__(self):
            self.textures = {}
            self.position = self.MikuProperties.k_start_position
            self.moving_to = self.MikuProperties.k_start_position
            self.__load_textures()
        
        def __load_textures(self):
            for texture_filename in os.listdir(self.MikuProperties.k_textures_folder):
                if texture_filename.find('.bmp') != -1:
                    texture_name = texture_filename.replace('.bmp','')
                    self.textures[texture_name] = Image.open(self.MikuProperties.k_textures_folder+'/'+texture_filename)

        def is_moving(self):
            return self.position != self.moving_to

        def walk(self):
            if (not self.is_moving()) and random.randint(1,self.MikuProperties.k_walking_prob) == 1:
                self.moving_to = [random.randint(-10,60),random.randint(8,17)]
            
            if self.position[0] < self.moving_to[0]:
                self.position[0] = self.position[0] + 1
            
            if self.position[1] < self.moving_to[1]:
                self.position[1] = self.position[1] + 1

            if self.position[0] > self.moving_to[0]:
                self.position[0] = self.position[0] - 1
            
            if self.position[1] > self.moving_to[1]:
                self.position[1] = self.position[1] - 1

        def process(self):
            self.walk()

        def draw(self,draw,image):
            miku_image = self.textures['miku_idle']

            if self.position[0] > self.moving_to[0]:
                miku_image = ImageOps.mirror(miku_image)
            
            image.paste(miku_image, tuple(self.position))

    def __init__(self,engine):
        self.engine = engine
        self.statusBar = self.StatusBar(engine)
        self.dock = self.Dock()
        self.miku = self.Miku()

    def process(self,engine):
        key_pressed = engine.input.getKey()
        if key_pressed == None:
            return

        if key_pressed['key'] == engine.input.Buttons.k_top:
            self.dock.next()
        elif key_pressed['key'] == engine.input.Buttons.k_bottom:
            self.dock.select(engine)

    def backgroundProcess(self,engine):
        None

    def draw(self):
        image = Image.new("1", (Display.k_width, Display.k_height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0,0,Display.k_width,Display.k_height), outline=255, fill=255)
        
        self.statusBar.draw(draw,image)
        self.dock.draw(draw,image)
        self.miku.process()
        self.miku.draw(draw,image)

        return image

