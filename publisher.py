import paho.mqtt.client as mqtt
import time
import datetime
import json
from decimal import Decimal

import busio
import board

import adafruit_tsl2591

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_tsl2591.TSL2591(i2c)

moisture = "50"
deviceId = "device1"

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
    "Date": datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
    "deviceId": deviceId
  }

  print(lux_value)
  return json.dumps(data)

def getMoisture():
  data = {
    "moisture": moisture,
    "Date": datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
    "deviceId": deviceId
  }
  return json.dumps(data)

client.loop_start()
while True:
  client.publish("device1/lux", payload=getLux(), qos=0)
  client.publish("device1/moisture", payload=getMoisture(), qos=0)
  time.sleep(2.0)
