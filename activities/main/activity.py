from PIL import Image, ImageDraw, ImageFont
from abstract import Activity, Display

class Main(Activity):
    def __init__(self):
        None

    def process(self,engine):
        print(engine.input.readBuffer())

    def draw(self):
        image = Image.new("1", (Display.k_width, Display.k_height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0,0,Display.k_width,Display.k_height), outline=255, fill=255)
        #draw.ellipse((5,5,40,40), outline=0, fill=255)
        draw.line((0,6,84,6), fill=0)
        return image

