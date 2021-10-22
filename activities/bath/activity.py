from abstract import Activity
from widgets import Battery, Clock
from PIL import Image

class Main(Activity):
    class BathConstants():
        k_textures_folder = './textures/bath'
        k_bath_texture = 'bath.bmp'
        k_bath_time = 6
        k_bath_heal = 30000

    def __init__(self,engine):
        self.engine = engine
        self.battery = Battery(engine)
        self.clock = Clock()
        self.time = self.BathConstants.k_bath_time
        self.bath_image = Image.open(self.BathConstants.k_textures_folder+'/'+self.BathConstants.k_bath_texture)

    def process(self,engine):
        if self.time == 0:
            miku = engine.getActivity('main').miku
            miku.addStatus('shower',self.BathConstants.k_bath_heal)
            engine.setActivity('main')
        
        self.time = self.time - 1

    def switch(self,engine):
        self.time = self.BathConstants.k_bath_time
        engine.setUpdatesPerSecond(1)

    def draw(self,draw,image):
        top = 2
        if self.time%2 == 0:
            top = 6

        image.paste(self.bath_image, (0,top))

        self.battery.draw(draw,image)
        self.clock.draw(draw,image)

        return image

