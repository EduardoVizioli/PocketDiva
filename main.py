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

#This is the engine, it is responsible for controling the activities and its tasks
class Engine():
    #The engine can run in two modes
    #pc mode = running on a pc, displaying on a window and receiving inputs from the keyboard.
    #pocket mode = running on a raspberry pi, displaying on a 84x48 PCD8544 display and receiving inputs from gpio buttons. (TODO)
    class EngineModes():
        k_mode_pocket = 0
        k_mode_pc = 1
    
    #Exception the engine can throw when something goes wrong.
    class EngineExceptions():
        class ActivityNotFound(Exception):
            None

    #Sets engine variables and defines the engine mode (PC or Pocket)
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
    
    #Sets de current activity that is being displayed to the user
    def setActivity(self,activity_name):
        try:
            activity = self.activities[activity_name]
            self.current_activity = activity_name
        except IndexError:
            raise EngineExceptions.ActivityNotFound

    #The main loop is responsible for processing, drawing and timming of the current activity.
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

    #The background processes run on a separate thread, it stays running all the time and is responsible for processing and timming of the modules background tasks.
    def _backgroundProcesses(self):
        while self.running:
            start = time.time()
            for activity_name in self.activities:
                self.activities[activity_name].backgroundProcess(self)
            end = time.time()
            wait = (1/self.background_updates_per_second)-(end-start)
            if wait > 0:
                time.sleep(wait)

    #Loads all activities into the memory and starts the thread for the background processes
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

    #Sends a signal to the engine to stop
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