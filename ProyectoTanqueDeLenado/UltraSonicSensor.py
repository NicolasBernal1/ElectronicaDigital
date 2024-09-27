"""
trigger: genera el ultrasonido
echo: recibe el ultrasonido

-el trigger.value va a empezar en 0
-para encender el trigger se prende por 10 micro segundos
-echo empieza en 0, al recibir una señal se vuelve 1
"""
from machine import Pin, Timer
import time
import _thread
import gc

class UltraSonicSensor:
    def __init__(self, triggerPin=25, echoPin=26):
        self.run = True
        self.triggerPin = triggerPin
        self.echoPin = echoPin
        self.trigger = Pin(self.triggerPin, Pin.OUT, Pin.PULL_DOWN)
        self.trigger.value(0)
        self.echo = Pin(self.echoPin,Pin.IN)
        print("[INFO] trigger / echo created")
        self.distance = 0
        _thread.start_new_thread(self.sound, ())
        
    def sound(self):
        while True:
            self.trigger.value(1)
            time.sleep(10e-6)
            self.trigger.value(0)
            
            while self.echo.value() == 0:
                pass
            
            count = 0
            while self.echo.value() == 1:
                time.sleep(1e-6)
                count += 1
            
            print(count)
            self.distance = ((0.5439 * count) + 5.9048)-10 #ajustar
            print(f"distance: {self.distance}")
            time.sleep(0.5)
            
            

if __name__ == "__main__":
    b = UltraSonicSensor()
    while True:
        time.sleep(1)
        b.sound()