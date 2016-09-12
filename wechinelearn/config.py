#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Config backend database connection
ref: http://docs.sqlalchemy.org/en/latest/core/engines.html
"""

# Using
host = r"C:\Users\shu\Documents\PythonWorkSpace\py3\py33_projects\wechinelearn-project\example\wechinelearn.sqlite"
port = None
username = None
password = None

# Database connection string
db_url = "sqlite:///%s" % host