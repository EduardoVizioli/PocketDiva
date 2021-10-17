from PIL import Image
from abstractClasses.activity import Activity
from abstractClasses.display import Display

class Main(Activity):
    def __init__(self):
        None

    def process(self,engine):
        None

    def draw(self):
        image = Image.new("1", (Display.k_width, Display.k_height))
        return image

