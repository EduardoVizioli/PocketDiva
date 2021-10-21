from abstract import Activity
import os

class Main(Activity):
    def __init__(self,engine):
        None

    def process(self,engine):
        None
            
    def backgroundProcess(self,engine):
        buttons = engine.background_data['buttons']
        for button in buttons:
            if button['key'] == engine.input.Buttons.k_top and button['time'] >= 3:
                engine.display.backlightToggle()

    def draw(self):
        return None

