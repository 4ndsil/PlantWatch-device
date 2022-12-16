from pymongo import MongoClient

connStr = "mongodb+srv://andsil:KYeQihkjxeL8H2j@plantwatch.tz71h9c.mongodb.net/?retryWrites=true&w=majority" 

client = MongoClient(connStr)

db = client["PlantWatch"]

lux = db.lux

moisture = db.moisture

def insert_lux(obj):
    lux.insert_one(obj)

def get_lux(deviceId):
    return list(lux.find({'deviceId': deviceId}))
    
def insert_moisture(obj):
    moisture.insert_one(obj)
    
def get_moisture(obj):
    return list(moisture.find({"deviceId": deviceId}))
