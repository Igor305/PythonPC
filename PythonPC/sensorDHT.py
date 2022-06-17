import pc_logging

import requests
import adafruit_dht
from board import *

def getSensorData():

    try:
        SENSOR_PIN = D22
        dht22 = adafruit_dht.DHT22(SENSOR_PIN, use_pulseio=False)
        data = (dht22.temperature - 2, dht22.humidity)

    except:
        data = (0,0)

    return data

def getTemperatureAndHumidity(apiStock, apiDeviceNumbers):

    try:
        _key = '28c9a7e466e042zc8e2q7de1392bb1w2'
        data = (0,0)

        while data == (0,0) :
            data = getSensorData()

        sensorData = 'http://ws05.avrora.lan/sensors/reg?key=' + _key + '&stock='+ apiStock + f'&sensor={apiDeviceNumbers}&temp={data[0]:.2f}&hum={data[1]:.2f}'

        responseSensorData = requests.get(sensorData)

        if (responseSensorData.status_code != 200):
            sensorData = 'http://ws06.avrora.lan/sensors/reg?key=' + _key + '&stock='+ apiStock + f'&sensor={apiDeviceNumbers}&temp={data[0]:.2f}&hum={data[1]:.2f}'
            responseSensorData = requests.get(sensorData)

            if (responseSensorData.status_code != 200):
                pc_logging.writeError("SensorDHT data were not sent")

    except Exception as error:
        pc_logging.writeError(f"SensorDHT data were not sent: {error}")

def getTemperatureCPU(apiStock, apiDeviceNumbers,tempCPU):

    try:
        _key = '28c9a7e466e042zc8e2q7de1392bb1w2'
        device = int(apiDeviceNumbers) + 100
        temp = f'{float(tempCPU):.2f}'
        sensorData = 'http://ws05.avrora.lan/sensors/reg?key=' + _key + '&stock='+ apiStock + f'&sensor={device}&temp={temp}&hum=0.00'

        responseSensorData = requests.get(sensorData)

        if (responseSensorData.status_code != 200):
            sensorData = 'http://ws06.avrora.lan/sensors/reg?key=' + _key + '&stock='+ apiStock + f'&sensor={device}&temp={temp}&hum=0.00'
            responseSensorData = requests.get(sensorData)

            if (responseSensorData.status_code != 200):
                pc_logging.writeError("SensorDHT data were not sent")

    except Exception as error:
        pc_logging.writeError(f"Temperature CPU data were not sent: {error}")