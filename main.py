from interfaces import PcDisplay, PcInput
from PIL import Image
import traceback
import threading
import time
import os

k_activities_folder = 'activities'
k_main_activity = 'main'
k_updates_per_second = 6
k_background_updates_per_second = 1

class Engine():
    class EngineModes():
        k_mode_pocket = 0
        k_mode_pc = 1
    
    class EngineExceptions():
        class ActivityNotFound(Exception):
            None

    def __init__(self,updates_per_second,background_updates_per_second,mode):
        self.running = False
        self.activities = {}
        self.current_activity = None
        self.backgroundThread = None
        self.updates_per_second = updates_per_second
        self.background_updates_per_second = background_updates_per_second

        if mode == self.EngineModes.k_mode_pc:
            self.display = PcDisplay()
            self.input = PcInput()
        else:
            raise NotImplementedError

        self._start()
    
    def setActivity(self,activity_name):
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
                activity.process(self)
                image = activity.draw()
                self.display.drawImage(image)

            end = time.time()
            wait = (1/self.updates_per_second)-(end-start)
            if wait > 0:
                time.sleep(wait)

    def _backgroundProcesses(self):
        while self.running:
            start = time.time()
            for activity_name in self.activities:
                self.activities[activity_name].backgroundProcess(self)
            end = time.time()
            wait = (1/self.background_updates_per_second)-(end-start)
            if wait > 0:
                time.sleep(wait)

    #Loads activities from the folder
    def _loadActivities(self):
        print('Loading activities...')
        for activity_name in os.listdir('./'+k_activities_folder):
            if activity_name.find('.') != -1:
                continue
            
            print(k_activities_folder+'.'+activity_name+'.activity')
            activity = __import__(k_activities_folder+'.'+activity_name+'.activity',fromlist=[None]).Main()
            print('Activity ('+activity_name+') loaded')
            self.activities[activity_name] = activity
        print('Starting background processes')
        self.backgroundThread = threading.Thread(target=self._backgroundProcesses, args=[])
        self.backgroundThread.start()
        print('Activities loaded.')

    def _stop(self):
        print('Exiting...')
        self.running = False
    
    #Initializes the engine
    def _start(self):
        try:
            self.running = True
            self._loadActivities()
            self.setActivity(k_main_activity)
            self._mainloop()
        except KeyboardInterrupt:
            self._stop()
        except:
            print('_______ERROR_______')
            traceback.print_exc()
            print('___________________')
            self._stop()

def main():
    engine = Engine(k_updates_per_second,k_background_updates_per_second,Engine.EngineModes.k_mode_pc)

if __name__ == '__main__':
    main()