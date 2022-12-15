import paho.mqtt.client as mqtt
import time
import datetime
import json

lux = "20000"
moisture = "50"
deviceId = "device1"

def on_connect(c, userdata, flags, rc):
  print("Connected")

client = mqtt.Client()
client.on_connect = on_connect

client.connect("localhost", 1883, 60)

def getLux():
  data = {
    "lux": lux,
    "Date": datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
    "deviceId": deviceId
  }
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