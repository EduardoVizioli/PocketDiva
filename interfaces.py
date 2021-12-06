from abstract import Display, Input, Battery
import numpy
import time

k_resize_factor = 5

class PcDisplay(Display):
    def __init__(self):
        self.backlight_status_on = False

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
        k_led = 16
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

    def __init__(self,engine):
        self.gpio = engine.gpio
        self.gpioSetup()
        self.spiSetup()
        self.buffer = [0] * (Display.k_width * Display.k_height // 8)
        self.reset()
        self.setBias(4)
        self.setContrast(60)
        self.displayBuffer()
        self.backlight_status_on = False
        self.backlightOn()
    
    def spiSetup(self):
        import spidev
        self.spidev = spidev
        self.device = spidev.SpiDev()
        self.device.open(self.SpiInfo.k_spi_port, self.SpiInfo.k_spi_device)
        self.device.max_speed_hz = self.SpiInfo.k_max_speed_hz
        self.device.mode = 0
        
    def gpioSetup(self):
        self.gpio.setup(self.SpiInfo.k_rst,self.gpio.OUT)
        self.gpio.setup(self.SpiInfo.k_dc,self.gpio.OUT)
        self.gpio.setup(self.SpiInfo.k_led,self.gpio.OUT)

    def reset(self):
        self.gpio.output(self.SpiInfo.k_rst,self.gpio.LOW)
        time.sleep(0.1)
        self.gpio.output(self.SpiInfo.k_rst,self.gpio.HIGH)
    
    def command(self, command):
        self.gpio.output(self.SpiInfo.k_dc,self.gpio.LOW)
        self.device.writebytes([command])

    def extendedCommand(self, command):
        #Set extended command mode
        self.command(self.DisplayCommands.k_pcd8544_functionset | self.DisplayCommands.k_pcd8544_extendedinstruction)

        #Sends command
        self.command(command)

        #Set normal display mode.
        self.command(self.DisplayCommands.k_pcd8544_functionset)
        self.command(self.DisplayCommands.k_pcd8544_displaycontrol | self.DisplayCommands.k_pcd8544_displaynormal)

    def setBias(self, bias):
        self.extendedCommand(self.DisplayCommands.k_pcd8544_setbias | bias)

    def setContrast(self, contrast):
        if contrast > 127:
            contrast = 127
        
        if contrast < 0:
            contrast = 0
        
        self.extendedCommand(self.DisplayCommands.k_pcd8544_setvop | contrast)
    
    def clear(self):
        self.buffer = [0] * (Display.k_width * Display.k_height // 8)

    def displayBuffer(self):
        self.command(self.DisplayCommands.k_pcd8544_setyaddr)
        self.command(self.DisplayCommands.k_pcd8544_setxaddr)
        # Write the buffer.
        self.gpio.output(self.SpiInfo.k_dc,self.gpio.HIGH)
        self.device.writebytes(self.buffer)

    def setDisplayInverted(self):
        self.command(self.DisplayCommands.k_pcd8544_displaycontrol | self.DisplayCommands.k_pcd8544_displayinverted)

    def setDisplayNormal(self):
        self.command(self.DisplayCommands.k_pcd8544_displaycontrol | self.DisplayCommands.k_pcd8544_displaynormal)

    def drawImage(self,image):
        if image.mode != '1':
            raise ValueError('Image must be in mode 1.')
        index = 0
        # Iterate through the 6 y axis rows.
        # Grab all the pixels from the image, faster than getpixel.
        pix = image.load()
        #Bank
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
        
        self.displayBuffer()

    def backlightOn(self):
        self.backlight_status_on = True
        self.gpio.output(self.SpiInfo.k_led,self.gpio.LOW)

    def backlightOff(self):
        self.backlight_status_on = False
        self.gpio.output(self.SpiInfo.k_led,self.gpio.HIGH)
    
    def backlightToggle(self):
        if self.backlight_status_on:
            self.backlightOff()
        else:
            self.backlightOn()

class PcInput(Input):
    def __init__(self):
        from pynput.keyboard import Key, Listener
        self.listener = Listener(on_press=self.keyPress,on_release=self.keyRelease) 
        self.listener.start()
        self.buffer = []
        self.background_buffer = []
        self.key_time = {}
        self.key = Key

    def keyPress(self,key):
        try:
            if self.key_time[key] == 0:
                self.key_time[key] = time.time()
        except KeyError:
            self.key_time[key] = time.time()

    def keyRelease(self,key):
        press_time = time.time() - self.key_time[key]
        self.key_time[key] = 0

        if key == self.key.up and self.Buttons.k_top not in self.buffer:
            self.buffer.append({'key':self.Buttons.k_top,'time':press_time})
            self.background_buffer.append({'key':self.Buttons.k_top,'time':press_time})
        elif key == self.key.down and self.Buttons.k_bottom not in self.buffer:
            self.buffer.append({'key':self.Buttons.k_bottom,'time':press_time})
            self.background_buffer.append({'key':self.Buttons.k_bottom,'time':press_time})

class RaspiInput(Input):
    class Buttons():
        k_top = 17
        k_bottom = 27

    def __init__(self,engine):
        self.gpio = engine.gpio
        self.gpio_buttons = [self.Buttons.k_top,self.Buttons.k_bottom]
        self.gpioSetup()
        self.buffer = []
        self.background_buffer = []
        self.noise_threshold = 0.01
        self.max_hold = 10

    def gpioSetup(self):
        for button in self.gpio_buttons:
            self.gpio.setup(button, self.gpio.IN, pull_up_down=self.gpio.PUD_DOWN)
            self.gpio.add_event_detect(button,self.gpio.RISING,callback=self.keyPress)

    def keyPress(self,key):
        start_time = time.time()

        #Wait for the button up
        while self.gpio.input(key) == 1:
            pass
        
        press_time = time.time() - start_time
        if press_time < self.max_hold and press_time > self.noise_threshold:
            if key == self.Buttons.k_top and self.Buttons.k_top not in self.buffer:
                key_data = {'key':self.Buttons.k_top,'time':press_time}
            elif key == self.Buttons.k_bottom and self.Buttons.k_bottom not in self.buffer:
                key_data = {'key':self.Buttons.k_bottom,'time':press_time}

            if not key_data['key'] in [k['key'] for k in self.buffer]:
                self.buffer.append(key_data)
            if not key_data['key'] in [k['key'] for k in self.background_buffer]:
                self.background_buffer.append(key_data)

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
        percentage = swapped/256
        if percentage > 100:
            percentage = 100
        return int(percentage)
        
