from interfaces import PcDisplay, PcInput, PcBattery, RaspiDisplay, RaspiInput, RaspiBattery
from PIL import Image
import traceback
import threading
import pickle
import time
import os

k_activities_folder = 'activities'
k_main_activity = 'clock'
k_data_folder = 'data'
k_updates_per_second = 4
k_background_updates_per_second = 1
k_autosave_interval_minutes = 5

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

    class Database():
        def __init__(self):
            None
        
        def store(self,folder,filename,obj):
            file = open('./'+k_data_folder+'/'+str(folder)+'/'+filename+'.bin', 'wb')
            pickle.dump(obj, file)
            file.close()
        
        def get(self,folder,filename):
            try:
                print('./'+k_data_folder+'/'+str(folder)+'/'+filename+'.bin')
                file = open('./'+k_data_folder+'/'+str(folder)+'/'+filename+'.bin', 'rb')
                data = pickle.load(file)
                file.close()
                return data
            except FileNotFoundError:
                return None

    #Sets engine variables and defines the engine mode (PC or Pocket)
    def __init__(self,mode):
        self.running = False
        self.activities = {}
        self.current_activity = None
        self.backgroundThread = None
        self.updates_per_second = None
        self.setUpdatesPerSecond(k_updates_per_second)
        self.background_data = {}
        self.database = self.Database()

        if mode == self.EngineModes.k_mode_pc:
            self.display = PcDisplay()
            self.input = PcInput()
            self.battery = PcBattery()
        else:
            import RPi.GPIO as GPIO
            self.gpio = GPIO
            self.gpio.setmode(self.gpio.BCM)
            self.gpio.setwarnings(False)
            self.display = RaspiDisplay(self)
            self.input = RaspiInput(self)
            self.battery = RaspiBattery()

        self._start()
    
    #Sets de current activity that is being displayed to the user
    def setActivity(self,activity_name):
        try:
            activity = self.activities[activity_name]
            activity.switch(self)
            self.current_activity = activity_name
        except KeyError:
            raise self.EngineExceptions.ActivityNotFound
        except IndexError:
            raise self.EngineExceptions.ActivityNotFound

    def getActivity(self,activity_name):
        try:
            return self.activities[activity_name]
        except KeyError:
            raise self.EngineExceptions.ActivityNotFound
        except IndexError:
            raise self.EngineExceptions.ActivityNotFound

    def setUpdatesPerSecond(self,upds):
        self.updates_per_second = upds

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
            wait = round((1/self.updates_per_second)-(end-start),5)
            if wait > 0:
                time.sleep(wait)

    #The background processes run on a separate thread, it stays running all the time and is responsible for processing and timming of the modules background tasks.
    def _backgroundProcesses(self):
        while self.running:
            start = time.time()
            buttons = self.input.getBackgroundBuffer()

            for activity_name in self.activities:
                self.background_data['buttons'] = buttons.copy()
                self.activities[activity_name].backgroundProcess(self)
            self._autosave()

            end = time.time()
            wait = round((1/k_background_updates_per_second)-(end-start),5)
            if wait > 0:
                time.sleep(wait)

    def _autosave(self):
        current_time = time.localtime()
        current_minute = int(time.strftime('%M',current_time))
        current_second = int(time.strftime('%S',current_time))

        if current_minute % k_autosave_interval_minutes == 0 and current_second == 0:
            print('autosave',time.strftime('%H:%M:%S',current_time))
            for activity_name in self.activities:
                self.activities[activity_name].save(self)

    #Loads all activities into the memory and starts the thread for the background processes
    def _loadActivities(self):
        print('Loading activities...')
        for activity_name in os.listdir('./'+k_activities_folder):
            if activity_name.find('.') != -1:
                continue
            
            print(k_activities_folder+'.'+activity_name+'.activity')
            activity = __import__(k_activities_folder+'.'+activity_name+'.activity',fromlist=[None]).Main(self)
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
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    try:
        uname = os.uname()
        if uname.nodename == 'raspberrypi':
            engine = Engine(Engine.EngineModes.k_mode_pocket)
        else:
            engine = Engine(Engine.EngineModes.k_mode_pc)
    except AttributeError:
        engine = Engine(Engine.EngineModes.k_mode_pc)
    
if __name__ == '__main__':
    main()