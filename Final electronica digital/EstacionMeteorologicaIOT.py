from machine import ADC, Pin, I2C
import time
from bmp280 import BMP280
import dht
import network
import mqttsenderv2
import json
import _thread
import gc

class WindDirectionSensor:
    def __init__(self, pin_adc=35, num_samples=100, adc_min=0, adc_max=4095, sender=None):
        self.pin_adc = pin_adc
        self.num_samples = num_samples
        self.adc_min = adc_min
        self.adc_max = adc_max
        self.value = 0
        self.direction = 0
        self.adc = ADC(Pin(self.pin_adc))
        self.adc.atten(ADC.ATTN_11DB)
        self.sender = sender

    def measure_samples(self):
        list_values = []
        for i in range(0, self.num_samples):
            self.value = self.adc.read()
            list_values.append(self.value)
            time.sleep(1e-3)
        list_values.sort()
        self.value = (list_values[self.num_samples // 2] + list_values[self.num_samples // 2 + 1]) / 2
        print("[INFO] ADC raw measurement (Wind Direction): {}".format(self.value))
        self.scale()
    
    def scale(self):
        self.direction = (self.value / self.adc_max) * 360
        print("[INFO] Wind Direction: {}°".format(self.direction)) #180° para el sur
        self.sender.send_data("wind-direction", self.direction)
        return self.direction


class WindSpeedSensor:
    def __init__(self, pin_pulses=14, sample_period=2, sender=None):
        self.pin_pulses = pin_pulses
        self.pulses = 0
        self.sample_period = sample_period
        self.wind_speed = 0
        self.pulse_pin = Pin(self.pin_pulses, Pin.IN)
        self.pulse_pin.irq(trigger=Pin.IRQ_RISING, handler=self.count_pulses)
        self.sender = sender
        
    def count_pulses(self, pin):
        self.pulses += 1
    
    def calculate_speed(self):
        # formula: V = P(2.25 / T)
        self.wind_speed = self.pulses * (2.25 / self.sample_period) * 0.447 #para pasar de mph a m/s
        self.pulses = 0  
        print("[INFO] Wind Speed: {} m/s".format(self.wind_speed))
        self.sender.send_data("wind-speed", self.wind_speed)
        return self.wind_speed


class BMP280Sensor:
    def __init__(self, i2c_scl=18, i2c_sda=5, sender=None):
        self.i2c = I2C(0, scl=Pin(i2c_scl, Pin.PULL_UP), sda=Pin(i2c_sda, Pin.PULL_UP))
        self.sensor = BMP280(self.i2c)
        self.temperature = 0
        self.pressure = 0
        self.sender = sender
    
    def read_temperature(self):
        self.temperature = self.sensor.temperature
        print("[INFO] Temperature: {} °C".format(self.temperature))
        self.sender.send_data("temperature", self.temperature)
        return self.temperature
    
    def read_pressure(self):
        self.pressure = self.sensor.pressure / 100
        print("[INFO] Pressure: {} hPa".format(self.pressure))
        self.sender.send_data("pressure", self.pressure)
        return self.pressure
    

class HumiditySensor:
    def __init__(self, pin=15, sender=None):
        self.humidity = 0
        self.sender = sender
        self.dht_sensor = dht.DHT11(Pin(pin))
    
    def read_humidity(self):
        self.dht_sensor.measure()
        self.humidity = self.dht_sensor.humidity()
        print("[INFO] Humidity: {} %".format(self.humidity))
        self.sender.send_data("humidity", self.humidity)
        return self.humidity


class WeatherStationIOT:
    def __init__(self, sender):
        self.sender = sender
        self.wind_direction_sensor = WindDirectionSensor(sender=self.sender)
        self.wind_speed_sensor = WindSpeedSensor(sender=self.sender)
        self.bmp280_sensor = BMP280Sensor(sender=self.sender)
        self.humidity_sensor = HumiditySensor(sender=self.sender)
        self.run = True
        _thread.start_new_thread(self.monitor, ())
        
    
    def monitor(self):
        while self.run:
            self.wind_direction_sensor.measure_samples()
            self.wind_speed_sensor.calculate_speed()
            self.bmp280_sensor.read_temperature()
            self.bmp280_sensor.read_pressure()
            self.humidity_sensor.read_humidity()
            gc.collect()
            time.sleep(2)
        self.sender.disconnect()
        
         
         
def connectWifi(ssid, password):
    nic = network.WLAN(network.STA_IF)
    nic.active(True)
    nic.connect(ssid, password)
    while not nic.isconnected():
        print("[INFO] Connecting to WiFi")
        time.sleep(1)
    print("[INFO] WiFi Connected")


if __name__ == "__main__":
    with open("mqttsender_config.json", "r") as file:  
        config = json.loads(file.read())
        ssid, password, client_id, token, device_label, server, port = (config[key] for key in ["ssid", "password", "client_id", "token", "device_label", "host", "port"])
        
    connectWifi(ssid, password)
    mqtt_sender = mqttsenderv2.MQTTSender(client_id, token, device_label, server, port)
    mqtt_sender.connect()
    gc.collect()
    
    station = WeatherStationIOT(mqtt_sender)
    while True:
        time.sleep(1)
    
