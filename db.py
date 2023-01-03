from pymongo import MongoClient
import os
import time

connStr = "mongodb+srv://andsil:KYeQihkjxeL8H2j@plantwatch.tz71h9c.mongodb.net/?retryWrites=true&w=majority" 

while True:
  try:
    client = MongoClient(connStr)
    break
  except:
   time.sleep(2)

db = client["PlantWatch"]

lux = db.lux

moisture = db.moisture

device = db.device

def insert_lux(obj):    
  lux.insert_one(obj)

def get_lux(deviceId):
    return list(lux.find({'deviceId': deviceId}))
    
def insert_moisture(obj):
    moisture.insert_one(obj)
    
def get_moisture(deviceId):
    return list(moisture.find({"deviceId": deviceId}))

def get_last_watered(deviceId):
    return list(moisture.find({"moisture": {"$gt": 800}}).sort("date", -1).limit(1))[0]["date"]

def get_device(deviceId):
    return device.find_one({"deviceId": deviceId})

print(get_last_watered("raspberry1"))


