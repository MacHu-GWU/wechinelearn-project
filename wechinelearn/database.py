#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
(
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


Work flow:

1. station
2. object
3. weather raw => weather data
4. object raw => object data
5. weather data + object data => feature raw
6. feature raw => feature
7. feature => machine learning model ...
"""

import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey, Index
from sqlalchemy import String, Integer, Float, DateTime, Boolean
from sqlalchemy import select, and_, func, distinct

from .config import db_url
    

db_url
engine = create_engine(db_url)
metadata = MetaData()

#--- Weather ---
# Station Meta Data
t_station = Table("station", metadata,
    Column("id", String, primary_key=True),
    Column("lat", Float),
    Column("lng", Float),
    # More attributes may added
)

# Weather Raw Data
# Label:
# - outdoorTemp: 1
# - solarPower: 2
# - windSpeed: 3
# - humidity: 4
# ...
t_weather_raw = Table("weather_raw", metadata,
    Column("station_id", String, ForeignKey("station.id"), primary_key=True),
    Column("time", DateTime, primary_key=True),
    Column("label", Integer, primary_key=True),
    Column("value", Float),
)

# Weather Data Interpolated
t_weather = Table("weather", metadata,
    Column("station_id", String, ForeignKey("station.id"), primary_key=True),
    Column("time", DateTime, primary_key=True),
    Column("outdoorTemp", Float),
    Column("outdoorTempReliab", Boolean),
    # More data points may added
)

#--- Object ---
# Object Meta Data
t_object = Table("object", metadata,
    Column("id", String, primary_key=True),
    Column("lat", Float),
    Column("lng", Float),
    # More attributes may added
)

# Object Raw Data
t_object_data_raw = Table("object_data_raw", metadata,
    Column("object_id", String, ForeignKey("object.id"), primary_key=True),
    Column("time", DateTime, primary_key=True),
    Column("label", Integer, primary_key=True),
    Column("value", Float),
)

# Object Data Interpolated
t_object_data = Table("object_data", metadata,
    Column("object_id", String, ForeignKey("object.id"), primary_key=True),
    Column("time", DateTime, primary_key=True),
    Column("load", Float),
    Column("loadReliab", Boolean),
    # More data points may added
)

#--- Feature ---
# Raw Feature Data, merged from Weather, Object
t_feature_raw = Table("feature_raw", metadata,
    Column("object_id", String, ForeignKey("object.id"), primary_key=True),
    Column("time", DateTime, primary_key=True),
    Column("hour", Integer),
    Column("is_weekend", Boolean),
    Column("outdoorTemp", Float),
    Column("load", Float),
)

# Feature Data, include derived feature
t_feature = Table("feature", metadata,
    Column("user_id", String, ForeignKey("station.id"), primary_key=True),
    Column("time", DateTime, primary_key=True),
    Column("hour", Integer),
    Column("is_weekend", Boolean),
    Column("outdoorTemp", Float),
    Column("outdoorTemp_1hourDelta", Float),
    Column("outdoorTemp_2hourDelta", Float),
    Column("outdoorTemp_3hourDelta", Float),
    Column("outdoorTemp_4hourDelta", Float),
    Column("outdoorTemp_1DayDelta", Float),
    Column("load", Float),
    Column("load_1hourDelta", Float),
    Column("load_2hourDelta", Float),
    Column("load_3hourDelta", Float),
    Column("load_4hourDelta", Float),
    Column("load_1DayDelta", Float),
)

metadata.create_all(engine)