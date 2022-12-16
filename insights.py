import time
import json
import db
import os
import datetime 

deviceId = os.environ.get("DEVICE_ID")

def moistureReasoning(sensorValue, apiValue):

    recommendedValues = [
        "Keep moist between watering & Can dry between watering",
        "Water when soil is half dry & Can dry between watering",
        "Water when soil is half dry & Change water regularly in the cup",
        "Keep moist between watering & Water when soil is half dry",
        "Keep moist between watering & Must not dry between watering",
        "Must dry between watering & Water only when dry",
        "Change water regularly in the cup & Water when soil is half dry"
    ];

    plantMoistureReport = {
        "Soil status": "",
        "Watering required": "",
    }

    if sensorValue < 560:
        plantMoistureReport["Soil status"] = "Very dry"

    if (559 < sensorValue) & (sensorValue < 920):
        plantMoistureReport["Soil status"] = "Dry"

    if (919 < sensorValue) & (sensorValue < 1280):
        plantMoistureReport["Soil status"] = "Half dry"

    if (1279 < sensorValue) & (sensorValue < 1640):
        plantMoistureReport["Soil status"] = "Moist"

    if (1639 < sensorValue) & (sensorValue < 2000):
        plantMoistureReport["Soil status"] = "Wet"

    if 1999 < sensorValue:
        plantMoistureReport["Soil status"] = "Just watered"

    if (apiValue == recommendedValues[0]) | (apiValue == recommendedValues[3]) | (apiValue == recommendedValues[4]):
        if sensorValue < 1279:
            plantMoistureReport["Watering required"] = "Yes <i class='bi bi-exclamation-triangle'></i>"
        else:
            plantMoistureReport["Watering required"] = "No"

    if (apiValue == recommendedValues[1]) | (apiValue == recommendedValues[2]) | (apiValue == recommendedValues[6]):
        if sensorValue < 919:
            plantMoistureReport["Watering required"] = "Yes <i class='bi bi-exclamation-triangle'></i>"
        else:
            plantMoistureReport["Watering required"] = "No"

    if apiValue == recommendedValues[5]:
        if sensorValue < 559:
            plantMoistureReport["Watering required"] = "Yes <i class='bi bi-exclamation-triangle'></i>"
        else:
            plantMoistureReport["Watering required"] = "No"
    return plantMoistureReport


def luxReasoning(sensorValue, apiValue):
    
    luxValues = db.get_lux(deviceId)
    
    times = lux_today(luxValues, apiValue)

    print(times)

    recommendedLuxValues = [
        "Diffuse light ( Less than 5,300 lux / 500 fc)",
        "Strong light ( 21,500 to 3,200 lux/2000 to 300 fc)",
        "Full sun (+21,500 lux /+2000 fc )",
    ];

    plantLightReport = {
        "Position status": "",
        "Light exposure": "",
    }

    if sensorValue < 5300:
        plantLightReport["Position status"] = "Diffuse light"

    if (5299 < sensorValue) & (sensorValue < 21500):
        plantLightReport["Position status"] = "Strong light"

    if 21499 < sensorValue:
        plantLightReport["Position status"] = "Full sun"

    if apiValue == recommendedLuxValues[0]:
        if sensorValue < 5300:
            plantLightReport["Light exposure"] = "Satisfied"
        else:
            plantLightReport["Light exposure"] = "Less light needed <i class='bi bi-exclamation-triangle'></i>"

    if apiValue == recommendedLuxValues[1]:
        if (5299 < sensorValue) & (sensorValue < 21500):
            plantLightReport["Light exposure"] = "Satisfied"
        elif sensorValue < 5230:
            plantLightReport["Light exposure"] = "More light needed <i class='bi bi-exclamation-triangle'></i>"
        elif 21499 < sensorValue:
            plantLightReport["Light exposure"] = "Less light needed <i class='bi bi-exclamation-triangle'></i>"

    if apiValue == recommendedLuxValues[2]:
        if 21499 < sensorValue:
            plantLightReport["Light exposure"] = "Satisfied"
        else:
            plantLightReport["Light exposure"] = "More light needed <i class='bi bi-exclamation-triangle'></i>"
    return plantLightReport

def lux_today(luxValues, apiValue):
  lux_dates = list(map(lambda lux: {"date": datetime.datetime.strptime(lux["date"], "%Y-%m-%d %H:%M:%S"),"lux": lux["lux"] }, luxValues))

  times = []

  total_time = 0

  for lux_date in lux_dates:
    if lux_date["date"].date() == datetime.date.today():
      times.append({"time": lux_date["date"],"lux": lux_date["lux"]})

  i = 1

  while i < len(times):
    print(times[i]["time"])
    if (getRecommendation(float(times[i]["lux"]), apiValue) == 1) & (getRecommendation(float(times[i -1]["lux"]), apiValue) == 1):
      print(times[i-1]["time"])
      delta = (times[i]["time"] - times[i-1]["time"]).total_seconds()      
      total_time += delta
    i += 1
  print("total time:", total_time)

def getRecommendation(sensorValue, apiValue):
  recommendedLuxValues = [
        "Diffuse light ( Less than 5,300 lux / 500 fc)",
        "Strong light ( 21,500 to 3,200 lux/2000 to 300 fc)",
        "Full sun (+21,500 lux /+2000 fc )",
    ];

    # 0 => more light needed
    # 1 => satisfied
    # 2 => less light needed

  if apiValue == recommendedLuxValues[0]:
    if sensorValue < 5300:
      return 1
    else:
      return 2
  if apiValue == recommendedLuxValues[1]:
    if (5299 < sensorValue) & (sensorValue < 21500):
      return 1
    elif sensorValue < 5230:
      return 0
    elif 21499 < sensorValue:
      return 2
  if apiValue == recommendedLuxValues[2]:
    if 21499 < sensorValue:
      return 1
    else:
      return 0
  raise ValueError("Error: Invalid api value.")
  
    


luxReasoning(5366, "Strong light ( 21,500 to 3,200 lux/2000 to 300 fc)")
