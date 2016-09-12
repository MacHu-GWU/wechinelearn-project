#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module defines the data schema. 

There are 8 major table used in this app. Let's go through them one by one.

database schema settings::

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

1. station metadata
2. object metadata
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

try:
    from .config import db_url
except:
    from wechinelearn.config import db_url
    
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
"""
A weather station must have id, lat, lng; Any observed weather data is associated
with a station.
"""

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
"""
Weather raw data table, data could be non-interpolated, sparse and arbitrary
many data points. For example, no matter how many data points we have, outdoorTemp,
solarPower, windSpeed, humidity, ..., etc, we put them here.
"""

# Weather Data Interpolated
t_weather = Table("weather", metadata,
    Column("station_id", String, ForeignKey("station.id"), primary_key=True),
    Column("time", DateTime, primary_key=True),
    Column("outdoorTemp", Float),
    Column("outdoorTempReliab", Boolean),
    # More data points may added
)
"""
This is processed weather data. All kinds of observation at same time will be 
put here. We put interpolated, processed here. Time axis has to be continues.
For those moment doesn't have valid data, we fill in with Null value.
"""

#--- Object ---
# Object Meta Data
t_object = Table("object", metadata,
    Column("id", String, primary_key=True),
    Column("lat", Float),
    Column("lng", Float),
    # More attributes may added
)
"""
Your analysis target. Must have lat, lng info. wechinelearn use this to local
couple of nearby stations and automatically find the best weather data.
"""

# Object Raw Data
t_object_data_raw = Table("object_data_raw", metadata,
    Column("object_id", String, ForeignKey("object.id"), primary_key=True),
    Column("time", DateTime, primary_key=True),
    Column("label", Integer, primary_key=True),
    Column("value", Float),
)
"""
Similar to weather raw data, but it's about your target.
"""

# Object Data Interpolated
t_object_data = Table("object_data", metadata,
    Column("object_id", String, ForeignKey("object.id"), primary_key=True),
    Column("time", DateTime, primary_key=True),
    Column("load", Float),
    Column("loadReliab", Boolean),
    # More data points may added
)
"""
Similar to weather data, it's interpolated, processed data.
"""

#--- Feature ---
# Raw Feature Data, merged from Weather, Object
t_feature_raw = Table("feature_raw", metadata,
    Column("object_id", String, ForeignKey("object.id"), primary_key=True),
    Column("time", DateTime, primary_key=True),
    Column("dayseconds", Float),
    Column("is_weekend", Boolean),
    Column("outdoorTemp", Float),
    Column("load", Float),
)
"""
This table is a result of merging weather and object data on the time axis.
This table only have data points you observed.
"""

# Feature Data, include derived feature
t_feature = Table("feature", metadata,
    Column("object_id", String, ForeignKey("object.id"), primary_key=True),
    Column("time", DateTime, primary_key=True),
    Column("dayseconds", Float),
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
"""
Sometimes you need to derive more features for your model. Then you need to 
take data out from ``feature_raw``, and even more from others, then put everything
here, so finally you have a nicely organized tabulate dataset. You can easily
choose any subset and plug in any machine learning model.
"""

metadata.create_all(engine)

if __name__ == "__main__":
    from datetime import datetime
    