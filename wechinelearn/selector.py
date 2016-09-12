#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

import heapq
import pandas as pd
from sqlalchemy import select, and_, func, distinct
from rolex import rolex
from sfm.geo_search import GeoSearchEngine
try:
    from .database import (
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
    from .munging import get_dayseconds
except:
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
    from wechinelearn.munging import get_dayseconds

train_data = list()
s = select([t_station])
for row in engine.execute(s):
    train_data.append(dict(row))
search_station = GeoSearchEngine("station")
search_station.train(
    data=train_data,
    key_id=lambda x: x["id"],
    key_lat=lambda x: x["lat"],
    key_lng=lambda x: x["lng"],
)

train_data = list()
s = select([t_object])
for row in engine.execute(s):
    train_data.append(dict(row))
search_object = GeoSearchEngine("object")
search_object.train(
    data=train_data,
    key_id=lambda x: x["id"],
    key_lat=lambda x: x["lat"],
    key_lng=lambda x: x["lng"],
)


class Selector(object):

    """Data selector interface.
    """

    def all_station_id(self):
        s = select([t_station.c.id])
        station_id_list = [row.id for row in engine.execute(s)]
        return station_id_list

    def all_object_id(self):
        s = select([t_object.c.id])
        object_id_list = [row.id for row in engine.execute(s)]
        return object_id_list

    def get_station_lat_lng(self, station_id):
        s = select([t_station]).where(t_station.c.id == station_id)
        row = engine.execute(s).fetchone()
        if row:
            return row.lat, row.lng
        else:
            raise ValueError("station_id(%r) not found!" % station_id)

    def get_object_lat_lng(self, object_id):
        s = select([t_object]).where(t_object.c.id == object_id)
        row = engine.execute(s).fetchone()
        if row:
            return row.lat, row.lng
        else:
            raise ValueError("object_id(%r) not found!" % object_id)

    def get_nearest_station(self, lat, lng):
        dist, station = search_station.find_n_nearest(lat, lng, n=1)[0]
        station_id = station["id"]
        return station_id

    def get_nearest_object(self, lat, lng):
        """

        **中文文档**

        获取某个坐标最近的object。
        """
        dist, object = search_object.find_n_nearest(lat, lng, n=1)[0]
        object_id = object["id"]
        return object_id

    def get_wdata_by_station(self, station_id, start, end):
        """

        **中文文档**

        获取一个气象站在某个时间段内所观测到的天气数据。
        """
        selected = [t_weather]
        filters = [
            t_weather.c.station_id == station_id,
            t_weather.c.time.between(
                rolex.parse_datetime(start),
                rolex.parse_datetime(end),
            ),
        ]
        s = select(selected).where(and_(*filters))
        df = pd.read_sql(s, engine)
        return df

    def get_wdata_by_coordinate(self,
                                lat, lng, start, end,
                                r1=0.95, radius1=60.0,
                                r2=0.75, radius2=30.0,
                                n_station=10):
        """
        
        **中文文档**
        
        选取某个坐标附近的天气数据。总是优先选择最可信的。若都不够95%可信,
        则可信度要优先于距离。

        这部分的算法稍微有些复杂, 详细逻辑如下:

        1. 从近到远地在radius1范围内选择气象站, 并对计算reliability, 若高于r1, 
          则返回该数据。即使后面可能有比r1可信度更高的数据, 也不采纳。
        2. 若果所有的气象站的reliability都无法高于r1, 那么选用radius2范围
          reliability最高的那个, 即使他离得较远。但是reliability至少要高于r2。
        """
        def cal_reliab(df):
            """Calculate reliability of a data chunk.
            """
            try:
                reliab_score = sum(df.outdoorTempReliab)/df.shape[0]
                return reliab_score
            except:
                return 0.0

        if radius1 < radius2:
            raise ValueError("radius1 has to be greater than radius2")

        res = search_station.find_n_nearest(
            lat, lng, n=n_station, radius=radius1)
        if len(res) == 0:
            raise ValueError(
                "No weather station found with in %s miles!" % radius1)

        round_2 = list()
        for dist, station in res:
            station_id = station["id"]
            df = self.get_wdata_by_station(station_id, start, end)

            try:
                reliab_score = cal_reliab(df)
                if reliab_score >= r1:
                    return df

                if (dist <= radius2) and (reliab_score >= r1):
                    round_2.append((reliab_score, df))
            except Exception as e:
                print(e)

        if len(round_2):
            res = heapq.nlargest(1, round_2, key=lambda x: x[0])
            reliab_score = res[0][0]
            df = res[0][1]
            return df

        raise ValueError("No valid weather data for (%s, %s)!" % (lat, lng))

    def get_wdata_by_object(self, object_id, start, end, **kwargs):
        """
        
        **中文文档**
        
        选取某个object附近的天气数据。总是优先选择最可信的。若都不够95%可信,
        则可信度要优先于距离。
        """
        lat, lng = self.get_object_lat_lng(object_id)
        try:
            return self.get_wdata_by_coordinate(lat, lng, start, end, **kwargs)
        except ValueError:
            raise

    def get_odata_by_object(self, object_id, start, end):
        """
        
        **中文文档**
        
        选取某个object某个时间段内的数据。
        """
        selected = [t_object_data]
        filters = [
            t_object_data.c.object_id == object_id,
            t_object_data.c.time.between(
                rolex.parse_datetime(start),
                rolex.parse_datetime(end),
            ),
        ]
        s = select(selected).where(and_(*filters))
        df = pd.read_sql(s, engine)
        return df

    def get_feature_raw(self, object_id, start, end):
        """
        
        **中文文档**
        
        选取某个object某个时间段内的特征。
        """
        selected = [t_feature_raw]
        filters = [
            t_feature_raw.c.object_id == object_id,
            t_feature_raw.c.time.between(
                rolex.parse_datetime(start),
                rolex.parse_datetime(end),
            ),
        ]
        s = select(selected).where(and_(*filters))
        df = pd.read_sql(s, engine)
        return df

    def get_feature(self, object_id, start, end):
        """
        
        **中文文档**
        
        选取某个object某个时间段内的特征。
        """
        selected = [t_feature]
        filters = [
            t_feature.c.object_id == object_id,
            t_feature.c.time.between(
                rolex.parse_datetime(start),
                rolex.parse_datetime(end),
            ),
        ]
        s = select(selected).where(and_(*filters))
        df = pd.read_sql(s, engine)
        return df

    #--- Forecasting Module Methods ---
    def get_useful_feature_data(self, object_id, date_time, features=None, label=None):
        """
        
        **中文文档**
        
        给定一个用户和时刻, 返回该时刻可用的所有特征数据。特征数据需要满足

        1. 31天以内的日期。
        2. 和该时刻同为工作日或周末。
        3. 小时的时差在2小时以内。

        返回numpy.ndarray
        """
        date_time = rolex.parse_datetime(date_time)
        start = rolex.add_days(date_time, -14)
        end = rolex.add_seconds(date_time, -1)
        is_weekend = date_time.isoweekday() in [6, 7]
        s = select([t_feature]).where(
            and_(
                t_feature.c.object_id == object_id,
                t_feature.c.time >= start,
                t_feature.c.time <= end,
                t_feature.c.is_weekend == is_weekend,
            )
        )
        df = pd.read_sql(s, engine)

        dayseconds = get_dayseconds(date_time)

        # closed time frame checker
        bandwidth = 2 * 3600
        h_low = bandwidth
        h_high = 24 * 3600 - bandwidth
        criterion = df["dayseconds"].map(
            lambda x: (
                abs(x - dayseconds) <= h_low) or (abs(x - dayseconds) >= h_high)
        )
        df = df[criterion]
        if features is None:
            features = ["outdoorTemp_1hourDelta", ]
        if label is None:
            label = "load_1hourDelta"

        train_data = df[features].values
        train_label = df[label].values

        return train_data, train_label

selector = Selector()

#--- Unittest ---


def test_selector():
    """
    """
    lat, lng = 32.7767, -96.7970  # Dallas
    station_id = "st-1"
    object_id = "obj-1"
    start, end = "2016-07-15 00:00:00", "2016-07-15 23:59:59"

    print(selector.all_station_id()[:5])  # 打印前5个station_id
    print(selector.all_object_id()[:5])  # 打印前5个object_id
    print(selector.get_station_lat_lng(station_id))
    print(selector.get_object_lat_lng(object_id))
    print(selector.get_nearest_station(lat, lng))
    print(selector.get_nearest_object(lat, lng))
    print(selector.get_wdata_by_station(station_id, start, end))
    print(selector.get_wdata_by_coordinate(lat, lng, start, end))
    print(selector.get_wdata_by_object(object_id, start, end))
    print(selector.get_odata_by_object(object_id, start, end))
    print(selector.get_feature_raw(object_id, start, end))
    print(selector.get_feature(object_id, start, end))
    print(selector.get_useful_feature_data(object_id, "2016-07-25 14:00:00"))

if __name__ == "__main__":
    test_selector()
