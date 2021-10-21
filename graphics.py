from PIL import Image
import os

k_font_dir = './textures/fonts'

class TextDraw():
    def __init__(self):
        self.textures = {}
        for texture_filename in os.listdir(k_font_dir):
            if texture_filename.find('.bmp') != -1:
                texture_name = texture_filename.replace('.bmp','')
                self.textures[texture_name] = Image.open(k_font_dir+'/'+texture_filename)

    def text(self,image,string,x,y,scale=1):
        text_image = None
        string = str(string)

        for char in string:
            if text_image:
                char_img = self.textures[char.lower()]
                new_img = Image.new('1', (char_img.width + text_image.width + 1, char_img.height),color=255)
                new_img.paste(text_image, (0,0))
                new_img.paste(char_img,(text_image.width + 1,0))
                text_image = new_img
            else:
                text_image = Image.open(k_font_dir+'/'+char.lower()+'.bmp')
        
        if scale != 1:
            text_image = text_image.resize((text_image.width*scale,text_image.height*scale))

        image.paste(text_image,(x,y))


        
