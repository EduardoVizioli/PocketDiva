from abstract import Activity
from widgets import Battery, Clock
from PIL import Image

class Main(Activity):
    class FoodConstants():
        k_textures_folder = './textures/food'
        k_burger_texture = 'burger.bmp'
        k_burger_time = 6
        k_burger_heal = 20000

    def __init__(self,engine):
        self.engine = engine
        self.battery = Battery(engine)
        self.clock = Clock()
        self.time = self.FoodConstants.k_burger_time
        self.burger_image = Image.open(self.FoodConstants.k_textures_folder+'/'+self.FoodConstants.k_burger_texture)

    def process(self,engine):
        if self.time == 0:
            miku = engine.getActivity('main').miku
            miku.addStatus('hunger',self.FoodConstants.k_burger_heal)
            engine.setActivity('main')
        
        self.time = self.time-1

    def switch(self,engine):
        self.time = self.FoodConstants.k_burger_time
        engine.setUpdatesPerSecond(1)

    def draw(self,draw,image):
        top = -2
        if self.time%2 == 0:
            top = 2

        image.paste(self.burger_image, (0,top))
        self.battery.draw(draw,image)
        self.clock.draw(draw,image)

        return image

