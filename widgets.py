from graphics import TextDraw
from PIL import Image, ImageOps
from utils import Utils
import random
import os

class Battery():
    def __init__(self,engine):
        self.engine = engine
        self.text_draw = TextDraw()
    
    def draw(self,draw,image):
        self.text_draw.text(image,self.engine.battery.getPercentage(),68,1)

class Clock():
    def __init__(self):
        from datetime import datetime
        self.datetime = datetime
        self.text_draw = TextDraw()

    def draw(self,draw,image):
        now = self.datetime.now()
        self.text_draw.text(image,now.strftime("%H@%M"),1,1)

class StatusBar():
    def __init__(self,engine):
        self.line = (0,7,84,7)
        self.clock = Clock()
        self.battery = Battery(engine)
        self.engine = engine
    
    def draw(self,draw,image):
        draw.line(self.line, fill=0)
        self.clock.draw(draw,image)
        self.battery.draw(draw,image)

class Miku():
    class MikuConstants():
        k_textures_folder = './textures/miku'
        k_data_folder = 'miku_data'
        k_data_filename = 'miku'
        k_start_position = [15,15]
        k_walking_prob = 15
        k_sleep_time = 10
        k_wake_up_time = 8
        k_status_complain = {
            'hunger':7200
        }
        k_maximum_status = {
            'hunger':43200,
            'shower':86400
        }
        
    def __init__(self,engine):
        self.textures = {}
        self.position = self.MikuConstants.k_start_position
        self.moving_to = self.MikuConstants.k_start_position
        self.current_texture = 'miku_idle'
        self.status = {}
        self._initialize_status()
        self._load_data(engine)
        self._load_textures()
    
    def _initialize_status(self):
        for status_name in self.MikuConstants.k_maximum_status:
            self.status[status_name] = self.MikuConstants.k_maximum_status[status_name]

    def _load_data(self,engine):
        last_status = engine.database.get(self.MikuConstants.k_data_folder,self.MikuConstants.k_data_filename)
        if last_status != None:
            for status in last_status:
                self.status[status] = last_status[status]

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

    def _walk(self):
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

    def _check_status(self):
        self.current_texture = 'miku_idle'
        
        if self.status['hunger'] < self.MikuConstants.k_status_complain['hunger']:
            self.current_texture = 'miku_hungry'

    def process(self):
        self._walk()
        self._check_status()

    def backgroundProcess(self,engine):
        for status_name in self.status:
            self.status[status_name] = self.status[status_name] - 1

    def draw(self,draw,image):
        miku_image = self.textures[self.current_texture]

        if self.position[0] > self.moving_to[0]:
            miku_image = ImageOps.mirror(miku_image)
        
        image.paste(miku_image, tuple(self.position))

    def save(self,engine):
        engine.database.store(self.MikuConstants.k_data_folder,self.MikuConstants.k_data_filename,self.status)