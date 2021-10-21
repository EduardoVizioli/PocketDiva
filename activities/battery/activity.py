from abstract import Activity
import os

class Main(Activity):
    def __init__(self,engine):
        self.engine = engine
        self.minimum_battery_level = 15

    def process(self,engine):
        None
            
    def backgroundProcess(self,engine):
        percent = self.engine.battery.getPercentage()
        if percent <= self.minimum_battery_level:
            os.system("sudo shutdown -h now")

    def draw(self):
        return None

