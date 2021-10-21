from abstract import Activity, Display
from PIL import Image, ImageDraw, ImageOps
from widgets import StatusBar
from graphics import TextDraw
from utils import Utils
import random
import json
import os

class Main(Activity):
    class Dock():
        def __init__(self):
            self.selected_action = 0
            self.dock_height = 10
            with open('./data/dock.json') as json_file:
                self.data = json.load(json_file)
            
            self.dock_actions_cnt = len(self.data['apps'])

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
                    image_space = int(((left_end-left_start)/2)-(activity_icon.width/2))
                    image.paste(activity_icon,(int(left_start)+image_space,int(bottom_end)+1))

    class Miku():
        class MikuConstants():
            k_textures_folder = './textures/miku'
            k_data_folder = 'miku_data'
            k_data_filename = 'miku'
            k_start_position = [15,15]
            k_walking_prob = 15
            k_sleep_time = 10
            k_wake_up_time = 8
            k_maximum_status = {'hunger':14400}
            
        def __init__(self,engine):
            self.textures = {}
            self.position = self.MikuConstants.k_start_position
            self.moving_to = self.MikuConstants.k_start_position
            self.status = {}
            self._initialize_status()
            self._load_data(engine)
            self._load_textures()
        
        def _initialize_status(self):
            for status_name in self.MikuConstants.k_maximum_status:
                self.status[status_name] = self.MikuConstants.k_maximum_status[status_name]

        def _load_data(self,engine):
            old_miku = engine.database.get(self.MikuConstants.k_data_folder,self.MikuConstants.k_data_filename)
            if old_miku != None:
                self.status = old_miku.status

        def _load_textures(self):
            for texture_filename in os.listdir(self.MikuConstants.k_textures_folder):
                if texture_filename.find('.bmp') != -1:
                    texture_name = texture_filename.replace('.bmp','')
                    self.textures[texture_name] = Image.open(self.MikuConstants.k_textures_folder+'/'+texture_filename)

        def addStatus(self,status_name,value):
            if self.status[status_name] + value > self.MikuConstants.k_maximum_status[status_name]:
                self.status[status_name] = self.MikuConstants.k_maximum_status[status_name]
            else:
                self.status[status_name] = self.status[status_name] + value

        def getStatus(self):
            return self.status

        def is_moving(self):
            return self.position != self.moving_to

        def walk(self):
            if (not self.is_moving()) and random.randint(1,self.MikuConstants.k_walking_prob) == 1:
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

        def backgroundProcess(self,engine):
            self.status['hunger'] = self.status['hunger'] - 1

        def draw(self,draw,image):
            miku_image = self.textures['miku_idle']

            if self.position[0] > self.moving_to[0]:
                miku_image = ImageOps.mirror(miku_image)
            
            image.paste(miku_image, tuple(self.position))

        def save(self,engine):
            engine.database.store(self.MikuConstants.k_data_folder,self.MikuConstants.k_data_filename,self)

    def __init__(self,engine):
        self.engine = engine
        self.statusBar = StatusBar(engine)
        self.dock = self.Dock()
        self.miku = self.Miku(engine)

    def process(self,engine):
        key_pressed = engine.input.getKey()
        if key_pressed == None:
            return

        if key_pressed['key'] == engine.input.Buttons.k_top:
            self.dock.next()
        elif key_pressed['key'] == engine.input.Buttons.k_bottom:
            self.dock.select(engine)

    def backgroundProcess(self,engine):
        self.miku.backgroundProcess(engine)

    def switch(self,engine):
        engine.setUpdatesPerSecond(4)

    def draw(self):
        image = Image.new("1", (Display.k_width, Display.k_height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0,0,Display.k_width,Display.k_height), outline=255, fill=255)
        
        self.statusBar.draw(draw,image)
        self.dock.draw(draw,image)
        self.miku.process()
        self.miku.draw(draw,image)

        return image

    def save(self,engine):
        self.miku.save(engine)
