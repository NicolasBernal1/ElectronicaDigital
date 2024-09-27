from  machine import ADC
import time
import _thread

class Voltmeter:
    def __init__(self, pin_adc=15, num_samples=100, adc_min=0, adc_max=1870, t_min=0, t_max = 150):
        self.pin_adc = pin_adc
        self.num_samples = num_samples
        self.adc_min = adc_min
        self.adc_max = adc_max
        self.t_min = t_min
        self.t_max = t_max
        self.value = 0
        self.temperature = 0
        self.adc = ADC(self.pin_adc)
        self.adc.atten(ADC.ATTN_11DB) #rango de operación del adc (hasta 2450mV)
        #hacer hilo para measure_samples
        _thread.start_new_thread(self.measure_samples, ())
        
        
    def measure(self):
        self.value = self.adc.read()
        print("[INFO] ADC measurement: {}".format(self.value))
    
    def measure_samples(self):
        while self.run:
            list_values = []
            for i in range(0, self.num_samples):
                self.value = self.adc.read()
                list_values.append(self.value)
                time.sleep(1e-3)
            list_values.sort()
            self.value = (list_values[self.num_samples//2] + list_values[self.num_samples//2 + 1])/2
            #print("[INFO] ADC list: {}".format(list_values))
            #print("[INFO] max difference : {}".format(100*(max(list_values)-min(list_values))/4095)+"%")
            print("[INFO] ADC measurement: {}".format(self.value))
            self.scale()
            time.sleep(0.5)
            
    def scale(self):
        m = (self.t_max - self.t_min)/(self.adc_max - self.adc_min)
        b = self.t_min - m*self.adc_min
        self.temperature = (m*self.value + b) #mV
        print("[INFO] Temperature: {} °".format(self.temperature))
        return self.temperature
        

if __name__ == "__main__":
    sensor_adc = Voltmeter()
    #
    while True:
        sensor_adc.measure_samples()
        time.sleep(1)
        

        
        
