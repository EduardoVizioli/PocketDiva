from graphics import TextDraw

class Battery():
    def __init__(self,engine):
        self.engine = engine
    
    def draw(self,draw,image):
        TextDraw.text(image,self.engine.battery.getPercentage(),68,1)

class Clock():
    def __init__(self):
        from datetime import datetime
        self.datetime = datetime
    
    def draw(self,draw,image):
        now = self.datetime.now()
        TextDraw.text(image,now.strftime("%H@%M"),1,1)

class StatusBar():
    def __init__(self,engine):
        self.line = (0,7,84,7)
        self.clock = Clock()
        self.battery = Battery(engine)
        self.engine = engine
    
    def draw(self,draw,image):
        draw.line(self.line, fill=0)
        self.clock.draw(draw,image)
        self.battery.draw(draw,image)