from abstract import Activity, Display
from PIL import Image, ImageOps
from widgets import StatusBar, Miku
import json

class Main(Activity):
    class Dock():
        def __init__(self):
            self.selected_action = 0
            self.dock_height = 10
            self.data_file = './data/dock.json'
            with open(self.data_file) as json_file:
                self.data = json.load(json_file)
            self.activity_icons = {}
            self._load_icons()
            self.dock_actions_cnt = len(self.data['apps'])

        def _load_icons(self):
            for app in self.data['apps']:
                try:
                    icon = Image.open('./activities/'+app+'/icon.bmp')
                    self.activity_icons[app] = {
                        'normal':icon,
                        'inverted':ImageOps.invert(icon)
                    }
                except FileNotFoundError:
                    self.activity_icons[app] = {
                        'normal':None,
                        'inverted':None
                    }

        def next(self):
            if self.selected_action < self.dock_actions_cnt - 1:
                self.selected_action = self.selected_action + 1
            else:
                self.selected_action = 0

        def select(self,engine):
            try:
                engine.setActivity(self.data['apps'][self.selected_action])
            except engine.EngineExceptions.ActivityNotFound:
                pass
        
        def draw(self,draw,image):
            for i in range(0,self.dock_actions_cnt):
                icon_width = (Display.k_width/self.dock_actions_cnt)
                left_start = i*icon_width
                left_end = left_start+icon_width
                bottom_start = Display.k_height-1
                bottom_end = Display.k_height-self.dock_height
                
                activity_icon = self.activity_icons[self.data['apps'][i]]['normal']
                fill = 255
                if i == self.selected_action:
                    fill = 0
                    activity_icon = activity_icon = self.activity_icons[self.data['apps'][i]]['inverted']
                
                if i == self.dock_actions_cnt-1:
                    left_end = left_end - 1
                
                draw.rectangle((left_start,bottom_start,left_end,bottom_end),outline=0,fill=fill)
                
                if activity_icon:
                    image_space = int(((left_end-left_start)/2)-(activity_icon.width/2))
                    image.paste(activity_icon,(int(left_start)+image_space,int(bottom_end)+1))

    def __init__(self,engine):
        self.engine = engine
        self.statusBar = StatusBar(engine)
        self.dock = self.Dock()
        self.miku = Miku(engine)

    def process(self,engine):
        self.miku.process()
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

    def draw(self,draw,image):
        self.statusBar.draw(draw,image)
        self.dock.draw(draw,image)
        self.miku.draw(draw,image)
        return image

    def save(self,engine):
        self.miku.save(engine)
