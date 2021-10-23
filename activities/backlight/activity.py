from abstract import Activity
import time

class Main(Activity):
    def __init__(self,engine):
        self.last_interaction = time.time()
        self.backlight_timeout = 15
        self.backlight_battery_percent_limit = 20
            
    def backgroundProcess(self,engine):
        buttons = engine.background_data['buttons']
        current_time = int(time.time())
        percent = engine.battery.getPercentage()
        if percent >= self.backlight_battery_percent_limit:
            if buttons != []:
                self.last_interaction = current_time
                if not engine.display.backlight_status_on:
                    engine.display.backlightOn()

        if engine.display.backlight_status_on and current_time > self.last_interaction + self.backlight_timeout:
            engine.display.backlightOff()

