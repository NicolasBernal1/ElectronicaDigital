import _thread
import time

class Pin:
    def __init__(self,n,s):
        self.n = n
        self.s = False


class UltraSoundSensor:
    def __init__(self):
        self.distance = 0
        _thread.start_new_thread(self.measureDistance(),())

    def measureDistance(self):
        while True:
            self.distance = time.strftime("%H:%M:%S", time.localtime())
            print(self.distance)
            time.sleep(1)
            
        
            

class TankController:
    def __init__(self, max_level=10, min_level=3):
        self.soundSensor = UltraSoundSensor()
        self.valve_in = Pin(1)
        self.valve_out = Pin(2)
        self.max_level = max_level
        self.min_level = min_level
        self.filling = False
        self.draining = False
    
    def fillTank(self):
        self.valve_in.s = True #abrir valvula
        self.filling = True
        while self.filling:
            if(self.soundSensor.distance >= self.max_level):
                self.filling = False
        self.valve_in.s = False #cerrar valvula

    def drainTank(self):
        self.valve_out.s = True #abrir valvula
        self.draining = True
        while self.draining:
            if(self.soundSensor.distance <= self.min_level):
                self.draining = False
        self.valve_out.s = False #cerrar valvula
    

    
TankController()
