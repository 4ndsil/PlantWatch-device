import time
import json
import db
import os
import datetime 
from enum import Enum

class lightNeeded(Enum):

    NEED_MORE = 0

    SATISFIED = 1

    NEED_LESS = 2

deviceId = os.environ.get("DEVICE_ID")

recommendedLuxValues = [
    "Diffuse light ( Less than 5,300 lux / 500 fc)",
    "Strong light ( 21,500 to 3,200 lux/2000 to 300 fc)",
    "Full sun (+21,500 lux /+2000 fc )",
];

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
    
    secondsToday = lux_today(luxValues, apiValue, datetime.date.today())
    secondsWeek = lux_today(luxValues, apiValue, datetime.date.today() - datetime.timedelta(days=7))
    seconds30 = lux_today(luxValues, apiValue, datetime.date.today() - datetime.timedelta(days=30))

    lightToday = checkLightHours(secondsToday, apiValue)
    lightWeek = checkLightHours(secondsWeek / 7, apiValue)
    light30 = checkLightHours(seconds30 / 30, apiValue)


    plantLightReport = {
        "Position status": "",
        "Light exposure": "",
        "Light today": lightToday,
        "Light week": lightWeek,
        "Light 30": light30
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

def lux_today(luxValues, apiValue, date):
  lux_dates = list(map(lambda lux: {"date": datetime.datetime.strptime(lux["date"], "%Y-%m-%d %H:%M:%S"),"lux": lux["lux"] }, luxValues))

  times = []

  total_time = 0

  for lux_date in lux_dates:
    if lux_date["date"].date() >= date:
      times.append({"time": lux_date["date"],"lux": lux_date["lux"]})

  i = 1
  
  while i < len(times):
    if (getRecommendation(float(times[i]["lux"]), apiValue) == 1) & (getRecommendation(float(times[i -1]["lux"]), apiValue) == 1):
      delta = (times[i]["time"] - times[i-1]["time"]).total_seconds()      
      total_time += delta
    i += 1
  print("total time:", total_time)
  return total_time

def checkLightHours (total_seconds, apiValue):
  full_shade = 10800
  full_sun = 21600
  if apiValue == recommendedLuxValues[0]:
    if total_seconds < full_shade:
        return {"status": lightNeeded.SATISFIED.name, "Light per day": total_seconds, "delta": 0}
    else:
        return {"status": lightNeeded.NEED_LESS.name, "Light per day": total_seconds, "delta": total_seconds-full_shade}
  elif apiValue == recommendedLuxValues[1]:
    if total_seconds < full_shade:
        return {"status": lightNeeded.NEED_MORE.name, "Light per day": total_seconds, "delta": full_shade-total_seconds}
    elif total_seconds > full_sun:
        return {"status": lightNeeded.NEED_LESS.name, "Light per day": total_seconds, "delta": total_seconds-full_sun}
    else:
        return {"status": lightNeeded.SATISFIED.name, "Light per day": total_seconds, "delta": 0}
  elif apiValue == recommendedLuxValues[2]:
    if total_seconds > full_sun:
        return {"status": lightNeeded.SATISFIED.name, "Light per day": total_seconds, "delta": 0}
    else:
        return {"status": lightNeeded.NEED_MORE.name, "Light per day": total_seconds, "delta": full_sun-total_seconds}


def getRecommendation(sensorValue, apiValue):
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
  
    


print(luxReasoning(5366, recommendedLuxValues[1]))

