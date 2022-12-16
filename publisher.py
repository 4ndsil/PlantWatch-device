import paho.mqtt.client as mqtt
import time
import datetime
import json
from decimal import Decimal
import db
import insights
import os

import busio
import board

import adafruit_tsl2591

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_tsl2591.TSL2591(i2c)

moisture = "50"
deviceId = os.environ.get("DEVICE_ID")

def on_connect(c, userdata, flags, rc):
  print("Connected")

client = mqtt.Client()
client.on_connect = on_connect

client.connect("localhost", 1883, 60)

def getLux():
  lux = sensor.lux
  lux_value = round(Decimal(lux), 3)
  data = {
    "lux": str(lux_value),
    "date": datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
    "deviceId": deviceId
  }
  return data

def getMoisture():
  data = {
    "moisture": moisture,
    "date": datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
    "deviceId": deviceId
  }
  return data

def getInsight():
    device = db.get_device(deviceId)    
    plant = json.loads(device["plant"])
    lux = getLux()
    moisture = getMoisture()
    luxReport = insights.luxReasoning(float(lux["lux"]), plant["Light ideal"])
    moistureReport = insights.moistureReasoning(float(moisture["moisture"]), plant["Watering"])    
    x =  {
          "luxReport": luxReport,
          "moistureReport": moistureReport,
          "lux": getLux(),
          "moisture": getMoisture()
        }
    
    return json.dumps(x)

client.loop_start()
while True:
  db.insert_lux(getLux())
  db.insert_moisture(getMoisture())
 # client.publish(deviceId, payload=getInsight(), qos=0)
 # print(getInsight())
  time.sleep(2.0)
