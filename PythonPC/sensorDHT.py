import pc_logging

import requests
import adafruit_dht
from board import *

def getSensorData():

    try:
        SENSOR_PIN = D22
        dht22 = adafruit_dht.DHT22(SENSOR_PIN, use_pulseio=False)
        data = (dht22.temperature, dht22.humidity)

    except:
        data = (0,0)
        
    return data

def getTemperatureAndHumidity(apiStock):
    
    try:
        _key = '28c9a7e466e042zc8e2q7de1392bb1w2'
        data = getSensorData()
        sensorData = 'http://ws05.avrora.lan/sensors/reg?key=' + _key + '&stock='+ apiStock + f'&sensor=1&temp={data[0]:.2f}&hum={data[1]:.2f}'
        responseSensorDAta = requests.get(sensorData)  

        if (responseSensorDAta.status_code != 200):
            sensorData = 'http://ws06.avrora.lan/sensors/reg?key=' + _key + '&stock='+ apiStock + f'&sensor=1&temp={data[0]:.2f}&hum={data[1]:.2f}'
            responseSensorDAta = requests.get(sensorData)  

            if (responseSensorDAta.status_code != 200):
                pc_logging.writeError("SensorDHT data were not sent")
    except:
        pc_logging.writeError("SensorDHT data were not sent")
