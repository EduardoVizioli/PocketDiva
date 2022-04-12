from abstract import Activity
from datetime import datetime, time

class Main(Activity):
    def __init__(self,engine):
        pass
            
    def backgroundProcess(self,engine):
        now = datetime.now().time()
        display = engine.display
        if (not display.getDisplayInverted()) and now >= time(19,00) and now <= time(8,00):
            display.setDisplayInverted()

