
import paho.mqtt.client as mqtt
import time
import datetime
import json
from decimal import Decimal
import db
import insights
import os
import copy
import busio
import board
from adafruit_seesaw.seesaw import Seesaw

import adafruit_tsl2591

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_tsl2591.TSL2591(i2c)
ss = Seesaw(i2c, addr=0x36)

moisture = "50"
deviceId = os.environ.get("DEVICE_ID")

def test():
  touch = ss.moisture_read()
  temp = ss.get_temp()
  print("temp: " + str(temp) + " moisture: " + str(touch))

def on_connect(c, userdata, flags, rc):
  print("Connected")

client = mqtt.Client()
client.on_connect = on_connect

client.connect("localhost", 1883, 60)

def getLux():
  lux = sensor.lux
  lux_value = round(Decimal(lux), 3)
  data = {
    "lux": int(lux_value),
    "date": datetime.datetime.today(),
    "deviceId": deviceId
  }
  
  db.insert_lux(copy.deepcopy(data))
  data["date"] = data["date"].strftime("%Y-%m-%d %H:%M:%S")
  return data

def getMoisture():
  moisture = ss.moisture_read()  
  data = {
    "moisture": int(moisture),
    "date": datetime.datetime.today(),
    "deviceId": deviceId
  }
  
  db.insert_moisture(copy.deepcopy(data))
  data["date"] = data["date"].strftime("%Y-%m-%d %H:%M:%S")
  return data

def getMoistureInsights():
  device = db.get_device(deviceId)
  plant = json.loads(device["plant"])
  moisture = getMoisture()
  moistureReport = insights.moistureReasoning(float(moisture["moisture"]), plant["Watering"])
  obj = {
	  "moistureReport": moistureReport,
 	  "moisture": getMoisture()
	}
  return json.dumps(obj)

def getLuxInsights():
    device = db.get_device(deviceId)    
    plant = json.loads(device["plant"])
    lux = getLux()
    luxReport = insights.luxReasoning(float(lux["lux"]), plant["Light ideal"])
    x = {
          "luxReport": luxReport,
          "lux": getLux()
        }
    
    return json.dumps(x)


client.loop_start()
while True:
  test()
  client.publish(deviceId + "/moisture", payload=getMoistureInsights(), qos=0)
  client.publish(deviceId + "/lux", payload=getLuxInsights(), qos=0)
  time.sleep(2.0)
