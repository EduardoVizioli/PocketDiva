from abstract import Activity
import time

class Main(Activity):
    def __init__(self,engine):
        self.last_interaction = int(time.time())
        self.lockscreen_timeout = 25
        self.lockscreen_activity = 'clock'
            
    def backgroundProcess(self,engine):
        buttons = engine.background_data['buttons']
        current_time = int(time.time())
        if buttons != []:
            self.last_interaction = current_time

        if current_time > self.last_interaction + self.lockscreen_timeout and engine.current_activity != self.lockscreen_activity:
            engine.setActivity(self.lockscreen_activity)

