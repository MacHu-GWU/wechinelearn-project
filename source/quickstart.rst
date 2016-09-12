Quick Start
===============================================================================
:mod:`wechinelearn.config.py <wechinelearn.config>` this file defines the back-end database your want to use. 

:mod:`wechinelearn.database.py <wechinelearn.database>` this file defines your data schema. We have 8 major table you need to work with.

- :any:`wechinelearn.database.t_station`: A weather station must have id, lat, lng; Any observed weather data is associated with a station.
- :any:`wechinelearn.database.t_weather_raw`: Weather raw data table, data could be non-interpolated, sparse and arbitrary many data points. For example, no matter how many data points we have, outdoorTemp, solarPower, windSpeed, humidity, ..., etc, we put them here.
- :any:`wechinelearn.database.t_weather`: This is processed weather data. All kinds of observation at same time will be  put here. We put interpolated, processed here. Time axis has to be continues. For those moment doesn't have valid data, we fill in with Null value.
- :any:`wechinelearn.database.t_object`: Your analysis target. Must have lat, lng info. wechinelearn use this to local couple of nearby stations and automatically find the best weather data.
- :any:`wechinelearn.database.t_object_data_raw`: Similar to weather raw data, but it's about your target.
- :any:`wechinelearn.database.t_object_data`: Similar to weather data, it's interpolated, processed data.
- :any:`wechinelearn.database.t_feature_raw`: This table is a result of merging weather and object data on the time axis. This table only have data points you observed.
- :any:`wechinelearn.database.t_feature`: Sometimes you need to derive more features for your model. Then you need to  take data out from ``feature_raw``, and even more from others, then put everything here, so finally you have a nicely organized tabulate dataset. You can easily choose any subset and plug in any machine learning model.

If you want to ...

- add more meta data about the weather station or your target, change ``t_station`` and ``t_object``.
- add more data points like `precipitation` for weather, or `age` for user, change ``t_weather``, ``t_object_data``. And for the same reason, you also need to update ``t_feature_raw`` and ``t_feature``.

Once you have filled your data into database (`here's an example how <https://github.com/MacHu-GWU/wechinelearn-project/blob/master/example/create.py>`_), you can use :mod:`wechinelearn.selector.py <wechinelearn.selector>` choose your train, test data, and test against your model.