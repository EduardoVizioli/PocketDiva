import time
import os

k_activities_folder = 'activities'
k_main_activity = 'main'

class Engine():
    class EngineModes():
        k_mode_pocket = 0
        k_mode_pc = 1
    
    class EngineExceptions():
        class ActivityNotFound(Exception):
            None

    def __init__(self,fps):
        self.running = False
        self.activities = {}
        self.current_activity = None
        self.fps = fps
        self._start()
    
    def set_activity(self,activity_name):
        try:
            activity = self.activities[activity_name]
            self.current_activity = activity_name
        except IndexError:
            raise EngineExceptions.ActivityNotFound


    #Main loop, all logic starts here
    def _mainloop(self):
        while self.running:
            start = time.time()
            if self.current_activity != None:
                activity = self.activities[self.current_activity]
                activity.process()
                image = activity.draw()
            
            for activity_name in self.activities:
                self.activities[activity_name].backgroundProcess()

            end = time.time()
            time.sleep((1/self.fps)-(end-start))

    #Loads activities from the folder
    def _load_activities(self):
        print('Loading activities...')
        for activity_name in os.listdir('./'+k_activities_folder):
            if activity_name[0] == '.':
                continue
            
            print(k_activities_folder+'.'+activity_name+'.activity')
            activity = __import__(k_activities_folder+'.'+activity_name+'.activity',fromlist=[None]).Main()
            print('Activity ('+activity_name+') loaded')
            self.activities[activity_name] = activity
        print('Activities loaded.')
    
    #Initializes the engine
    def _start(self):
        self.running = True
        self._load_activities()
        self.set_activity(k_main_activity)
        self._mainloop()

def main():
    engine = Engine(3)

if __name__ == '__main__':
    main()