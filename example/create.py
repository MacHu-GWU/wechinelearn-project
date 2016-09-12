#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from datetime import datetime
from sqlalchemy import select
import pandas as pd
from sfm.sqlalchemy_mate import smart_insert
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
from wechinelearn.munging import get_dayseconds, difference
from wechinelearn.selector import selector


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
    """Create some dummy weather data.
    """
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
    """Create some dummy object data.
    """
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

def feed_t_feature_raw():
    """Merge t_weather and t_object_data into t_feature_raw
    """
    engine.execute(t_feature_raw.delete())
    for object_id in selector.all_object_id():
        print("Processing object_id(%s)" % object_id)
        try:
            df_w = selector.get_wdata_by_object(object_id, start, end)
            df_o = selector.get_odata_by_object(object_id, start, end)
            df = pd.merge(df_w, df_o, on="time", how="right")
            df["dayseconds"] = df.time.apply(get_dayseconds)
            df["is_weekend"] = [dt.isoweekday() in [6, 7] for dt in df.time]
            del df["station_id"]
            del df["outdoorTempReliab"]
            del df["loadReliab"]
            df.to_sql(t_feature_raw.name, engine, if_exists="append", index=False)
            print("  Success!")
        except Exception as e:
            print("  Failed! %s" % e)
          
# feed_t_feature_raw()

def feed_t_feature():
    """Take raw feature, and derive some new feature.
    """
    engine.execute(t_feature.delete())
    for object_id in selector.all_object_id():
        print("Processing object_id(%s)" % object_id)
        df = selector.get_feature_raw(object_id, start, end)
        try:
            df["outdoorTemp_1hourDelta"] = [None,] * 1 + difference(df.outdoorTemp, 1)
            df["outdoorTemp_2hourDelta"] = [None,] * 2 + difference(df.outdoorTemp, 2)
            df["outdoorTemp_3hourDelta"] = [None,] * 3 + difference(df.outdoorTemp, 3)
            df["outdoorTemp_4hourDelta"] = [None,] * 4 + difference(df.outdoorTemp, 4)
            df["outdoorTemp_1DayDelta"] = [None,] * 24 + difference(df.outdoorTemp, 24)
            
            df["load_1hourDelta"] = [None,] * 1 + difference(df.load, 1)
            df["load_2hourDelta"] = [None,] * 2 + difference(df.load, 2)
            df["load_3hourDelta"] = [None,] * 3 + difference(df.load, 3)
            df["load_4hourDelta"] = [None,] * 4 + difference(df.load, 4)
            df["load_1DayDelta"] = [None,] * 24 + difference(df.load, 24)
            df.to_sql(t_feature.name, engine, if_exists="append", index=False)
            print("  Success!")
        except Exception as e:
            print("  Failed! %s" % e)
            
feed_t_feature()
