from abstract import Display, Input, Battery
import numpy
import time

k_resize_factor = 5

class PcDisplay(Display):
    def __init__(self):
        None

    def drawImage(self,image):
        import cv2
        image = image.resize((Display.k_width*k_resize_factor,Display.k_height*k_resize_factor))
        array = numpy.float32(image) 
        cv_image = cv2.cvtColor(array, cv2.CV_8UC1)
        cv2.imshow("Pocket Diva", cv_image)
        key = cv2.waitKey(1)
        if cv2.getWindowProperty('Pocket Diva', 0) == -1:
            raise KeyboardInterrupt

class RaspiDisplay(Display):
    class SpiInfo():
        k_dc = 23
        k_rst = 24
        k_spi_port = 0
        k_spi_device = 0
        k_max_speed_hz = 4000000

    class DisplayCommands():
        k_pcd8544_powerdown = 0x04
        k_pcd8544_entrymode = 0x02
        k_pcd8544_extendedinstruction = 0x01
        k_pcd8544_displayblank = 0x0
        k_pcd8544_displaynormal = 0x4
        k_pcd8544_displayallon = 0x1
        k_pcd8544_displayinverted = 0x5
        k_pcd8544_functionset = 0x20
        k_pcd8544_displaycontrol = 0x08
        k_pcd8544_setyaddr = 0x40
        k_pcd8544_setxaddr = 0x80
        k_pcd8544_settemp = 0x04
        k_pcd8544_setbias = 0x10
        k_pcd8544_setvop = 0x80

    def __init__(self):
        import spidev
        import RPi.GPIO as GPIO
        self.gpio = GPIO
        self.gpio.setmode(self.gpio.BCM)
        self.gpio.setwarnings(False)
        self.gpio.setup(self.SpiInfo.k_rst,self.gpio.OUT)
        self.gpio.setup(self.SpiInfo.k_dc,self.gpio.OUT)
        self.spidev = spidev
        self.device = spidev.SpiDev()
        self.device.open(self.SpiInfo.k_spi_port, self.SpiInfo.k_spi_device)
        self.device.max_speed_hz = self.SpiInfo.k_max_speed_hz
        self.device.mode = 0
        #self.device.cshigh = False
        self.buffer = [0] * (Display.k_width * Display.k_height // 8)
        self.reset()
        self.set_bias(4)
        self.set_contrast(60)
        self.display_buffer()
    
    def reset(self):
        self.gpio.output(self.SpiInfo.k_rst,self.gpio.LOW)
        time.sleep(0.1)
        self.gpio.output(self.SpiInfo.k_rst,self.gpio.HIGH)
    
    def command(self, command):
        self.gpio.output(self.SpiInfo.k_dc,self.gpio.LOW)
        self.device.writebytes([command])

    def extended_command(self, command):
        #Set extended command mode
        self.command(self.DisplayCommands.k_pcd8544_functionset | self.DisplayCommands.k_pcd8544_extendedinstruction)

        #Sends command
        self.command(command)

        #Set normal display mode.
        self.command(self.DisplayCommands.k_pcd8544_functionset)
        self.command(self.DisplayCommands.k_pcd8544_displaycontrol | self.DisplayCommands.k_pcd8544_displaynormal)

    def set_bias(self, bias):
        self.extended_command(self.DisplayCommands.k_pcd8544_setbias | bias)

    def set_contrast(self, contrast):
        if contrast > 127:
            contrast = 127
        
        if contrast < 0:
            contrast = 0
        
        self.extended_command(self.DisplayCommands.k_pcd8544_setvop | contrast)
    
    def clear(self):
        self.buffer = [0] * (Display.k_width * Display.k_height // 8)

    def display_buffer(self):
        self.command(self.DisplayCommands.k_pcd8544_setyaddr)
        self.command(self.DisplayCommands.k_pcd8544_setxaddr)
        # Write the buffer.
        self.gpio.output(self.SpiInfo.k_dc,self.gpio.HIGH)
        self.device.writebytes(self.buffer)

    def set_display_inverted(self):
        self.command(self.DisplayCommands.k_pcd8544_displaycontrol | self.DisplayCommands.k_pcd8544_displayinverted)

    def set_display_normal(self):
        self.command(self.DisplayCommands.k_pcd8544_displaycontrol | self.DisplayCommands.k_pcd8544_displaynormal)

    def drawImage(self,image):
        if image.mode != '1':
            raise ValueError('Image must be in mode 1.')
        index = 0
        # Iterate through the 6 y axis rows.
        # Grab all the pixels from the image, faster than getpixel.
        pix = image.load()
        for row in range(6):
            # Iterate through all 83 x axis columns.
            for x in range(84):
                # Set the bits for the column of pixels at the current position.
                bits = 0
                # Don't use range here as it's a bit slow
                for bit in [0, 1, 2, 3, 4, 5, 6, 7]:
                    bits = bits << 1
                    bits |= 1 if pix[(x, row*self.k_rowpixels+7-bit)] == 0 else 0
                # Update buffer byte and increment to next byte.
                self.buffer[index] = bits
                index += 1
        
        self.display_buffer()

class PcInput(Input):
    def __init__(self):
        from pynput.keyboard import Key, Listener
        self.listener = Listener(on_press=self.key_press,on_release=self.key_release) 
        self.listener.start()
        self.buffer = []
        self.key_time = {}
        self.key = Key

    def key_press(self,key):
        try:
            if self.key_time[key] == 0:
                self.key_time[key] = time.time()
        except KeyError:
            self.key_time[key] = time.time()

    def key_release(self,key):
        press_time = time.time() - self.key_time[key]
        self.key_time[key] = 0

        if key == self.key.up and self.Buttons.k_top not in self.buffer:
            print('up')
            self.buffer.append({'key':self.Buttons.k_top,'time':press_time})
        elif key == self.key.down and self.Buttons.k_bottom not in self.buffer:
            self.buffer.append({'key':self.Buttons.k_bottom,'time':press_time})
        
    def readBuffer(self):
        buffer = self.buffer.copy()
        self.buffer = []
        return buffer
    
    def getKey(self):
        try:
            return self.buffer.pop()
        except IndexError:
            return None

class RaspiInput(Input):
    class Buttons():
        k_top = 17
        k_bottom = 27

    def __init__(self):
        import RPi.GPIO as GPIO
        self.gpio = GPIO
        self.gpio_buttons = [self.Buttons.k_top,self.Buttons.k_bottom]
        self.gpio_setup()
        self.buffer = []
        self.noise_threshold = 0.01
        self.max_hold = 10

    def gpio_setup(self):
        self.gpio.setwarnings(False)
        self.gpio.setmode(self.gpio.BCM)
        for button in self.gpio_buttons:
            self.gpio.setup(button, self.gpio.IN, pull_up_down=self.gpio.PUD_DOWN)
            self.gpio.add_event_detect(button,self.gpio.RISING,callback=self.key_press)

    def key_press(self,key):
        start_time = time.time()

        while self.gpio.input(key) == 1: # Wait for the button up
            pass
            
        press_time = time.time() - start_time
        if press_time < self.max_hold and press_time > self.noise_threshold:
            print(press_time)
            if key == self.Buttons.k_top and self.Buttons.k_top not in self.buffer:
                self.buffer.append({'key':self.Buttons.k_top,'time':press_time})
            elif key == self.Buttons.k_bottom and self.Buttons.k_bottom not in self.buffer:
                self.buffer.append({'key':self.Buttons.k_bottom,'time':press_time})

    def readBuffer(self):
        buffer = self.buffer.copy()
        self.buffer = []
        return buffer
    
    def getKey(self):
        try:
            return self.buffer.pop()
        except IndexError:
            return None


class PcBattery(Battery):
    def __init__(self):
        import psutil
        self.psutil = psutil
    
    def getPercentage(self):
        return int(self.psutil.sensors_battery().percent)

class RaspiBattery(Battery):
    def __init__(self):
        import smbus
        import struct
        self.smbus = smbus
        self.struct = struct
        self.bus = self.smbus.SMBus(1)
    
    def getPercentage(self):
        #This function returns as a float the remaining capacity of the battery connected to the Raspi UPS Hat via the provided SMBus object"
        address = 0x36
        read = self.bus.read_word_data(address, 0X04)
        swapped = self.struct.unpack("<H", self.struct.pack(">H", read))[0]
        capacity = swapped/256
        return int(capacity)
