from voltmeter import Voltmeter
from UltraSonicSensor import UltraSonicSensor
import time
import _thread
from machine import Pin

class LevelController:
    def __init__(self):
        self.sensor_ultrasonido = UltraSonicSensor()  #distancia


class TankController:
    def __init__(self, filling_valve_pin=2, draining_valve_pin=4, start_filling_pin=32,start_draining_pin=33,stop_pin=35 ,max_temp=90, max_level=15, min_level=5, tank_height=20):
        #objects
        self.level = LevelController()
        self.temperature_controller = Voltmeter()
        #hardware and hardware preparation
        self.filling_valve = Pin(filling_valve_pin, Pin.OUT)#pin 2
        self.filling_valve.value(0)
        
        self.draining_valve = Pin(draining_valve_pin, Pin.OUT)#pin 4
        self.draining_valve.value(0)
        
        self.start_filling_button = Pin(start_filling_pin, Pin.IN, Pin.PULL_DOWN)#pin 32
        self.start_filling_button = Pin(start_draining_pin, Pin.IN, Pin.PULL_DOWN)#pin 33
        self.stop_button = Pin(stop_pin, Pin.IN, Pin.PULL_DOWN)#pin 35
        #process controllers
        self.filling = False
        self.draining = False
        self.top = tank_height - max_level
        self.bottom = tank_height - min_level
        
        #temp control
        _thread.start_new_thread(self.temperatureFail, ())
        
        #button control
        self.start_filling_button.irq(trigger=Pin.IRQ_RISING, handler=self.start_filling_irq)
        self.start_draining_button.irq(trigger=Pin.IRQ_RISING, handler=self.start_draining_irq)
        self.stop_button.irq(trigger=Pin.IRQ_RISING, handler=self.stop_irq)
        
        
    
    def startFilling(self):
        self.filling_valve.value(1)
        self.filling = True
        print("[INFO] Filling the tank")
        while self.filling:
            if(self.level.distance <= self.top):
                self.filling = False
        self.filling_valve.value(0)
        print("[INFO] Tankk filled")
    
    def startDraining(self):
        self.draining_valve.value(1)
        self.draining = True
        print("[INFO] Draining the tank")
        while self.draining:
            if(self.level.distance >= self.bottom):
                self.draining = False
        self.draining_valve.value(0)
        print("[INFO] Tank drained")
    
    def stopProcess(self):
        self.draining = False
        self.draining_valve.value(0)
        self.filling = False
        self.filling_valve.value(0)
        print("[INFO] All processes stopped")
    
    def temperatureFail(self):
        while True:
            if(self.temperature_controller.temperature >= max_temp):
                self.stopProcess()
            time.sleep(0.5)
    

#3 botones, un sensor ultrasonico, un sensor de temperatura, un microcontrolador, 2 leds
#sensor de temperatura 5vin, 1.5 maxvout