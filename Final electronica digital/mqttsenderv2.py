import time
from umqttsimple import MQTTClient, MQTTException
import machine
import ubinascii
import json
import network

class MQTTSender:
    def __init__(self, client_id, token, device_label, server, port):
        self.client = MQTTClient(client_id, server, port, user=token, password="")
        self.device_label = device_label
        self.is_connected = False
        


    def connect(self):
        try:
            self.client.connect()
            print("[INFO] Connected")
            self.is_connected = True
        except Exception as e:
            print("[ERROR] No se pudo conectar: ", e)
    
    def disconnect(self):
        if self.is_connected:
            self.client.disconnect()
            print("[INFO] Desconectado de Ubidots")
            self.is_connected = False
        else:
            print("[INFO] Not connected!")
            

    def send_data(self, variable, value):
        if self.is_connected:
            topic = f"/v1.6/devices/{self.device_label}"
            payload = json.dumps({variable: value})
            try:
                self.client.publish(topic, payload)
                print(f"[INFO] Publicado en Ubidots: {payload}")
            except Exception as e:
                print("[ERROR] No se pudo enviar el dato: ", e)
        else:
            print("[INFO] Cant send data without connection!")
    
    def keep_alive(self):
        try:
            self.client.ping()
            print("[INFO] Conexión mantenida activa")
        except Exception as e:
            print("[ERROR] Error al mantener conexión: ", e)

# Ejemplo de uso
if __name__ == "__main__":
    def connectWifi(ssid, password):
        nic = network.WLAN(network.STA_IF)
        nic.active(True)
        nic.connect(ssid, password)
        while not nic.isconnected():
            print("[INFO] Connecting to WiFi")
            time.sleep(1)
        print("[INFO] WiFi Connected")
        
        with open("mqttsender_config.json", "r") as file:  
            config = json.loads(file.read())
            ssid, password, client_id, token, device_label, server, port = (config[key] for key in ["ssid", "password", "client_id", "token", "device_label", "host", "port"]) 
        
    connectWifi(ssid, password)


    mqtt_sender = MQTTSender(client_id, token, device_label, server, port)
    mqtt_sender.connect()

    # Envía datos
    mqtt_sender.send_data("temperature", 27)
    #mqtt_sender.send_data("pressure", 1013)

    # Desconectar cuando se termine
    time.sleep(5)
    mqtt_sender.disconnect()
