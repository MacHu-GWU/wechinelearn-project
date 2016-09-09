#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from datetime import datetime
from sqlalchemy import select

from sfm import rnd
from rolex import rolex
from uszipcode import ZipcodeSearchEngine
from wechinelearn.database import (
    engine,
    t_station, 
    t_weather_raw, 
    t_weather,
    t_object, 
    t_object_data_raw,
    t_object_data,
    t_feature_raw, 
    t_feature,
)

def rnd_high_low_1():
    return random.random() * 2 - 1


# 所有的station和object都在Dallas TX附近
lat, lng = 32.7767, -96.7970 # Dallas TX
start = rolex.parse_datetime("2016-07-01 00:00:00")
end = rolex.parse_datetime("2016-07-31 23:59:59")
timeAxis = rolex.time_series(start, end, freq="1hour")

def feed_t_station():
    se = ZipcodeSearchEngine()
    # zipcode in 150 miles
    z_50 = random.sample(se.by_coordinate(lat, lng, 150, returns=9999), 50)
    data = list()
    for i, z in enumerate(z_50):
        row = {
            "id": "st-%s" % i, 
            "lat": z.Latitude + rnd_high_low_1() * 0.01, 
            "lng": z.Longitude + rnd_high_low_1() * 0.01,
        }
        data.append(row)
    engine.execute(t_station.insert(), data)

# feed_t_station()

def feed_t_weather():
    data = list()
    for station in engine.execute(select([t_station])).fetchall():
        for time in timeAxis:
            row = {
                "station_id": station.id,
                "time": time,
                "outdoorTemp": random.random(),
                "outdoorTempReliab": 1,
            }
            data.append(row)
    
    engine.execute(t_weather.insert(), data)
    
# feed_t_weather()

def feed_t_object():
    se = ZipcodeSearchEngine()
    z_list = se.by_coordinate(lat, lng, 200, returns=9999) # zipcode in 200 miles
    z_50 = [random.choice(z_list) for i in range(200)]
    data = list()
    for i, z in enumerate(z_50):
        i += 1
        row = {
            "id": "obj-%s" % i, 
            "lat": z.Latitude + rnd_high_low_1() * 0.05, 
            "lng": z.Longitude + rnd_high_low_1() * 0.05,
        }
        data.append(row)
    engine.execute(t_object.insert(), data)

# feed_t_object()

def feed_t_object_data():
    data = list()
    for obj in engine.execute(select([t_object])).fetchall():
        for time in timeAxis:
            row = {
                "object_id": obj.id,
                "time": time,
                "load": random.random(),
                "loadReliab": 1,
            }
            data.append(row)
            
    engine.execute(t_object_data.insert(), data)
    
# feed_t_object_data()

def feed_t_feature():
    data = list()
    for obj in engine.execute(select)
    
feed_t_feature()