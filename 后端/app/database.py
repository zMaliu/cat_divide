# -*- coding: utf-8 -*-
import pymysql
import os
from dbutils.pooled_db import PooledDB

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'Zykhoainng0527.'),
    'database': os.environ.get('DB_NAME', 'cat'),
    'charset': "utf8mb4",
    'autocommit': False,
    'cursorclass': pymysql.cursors.DictCursor
}

print(f"数据库配置: {DB_CONFIG}")

pool = PooledDB(
    creator=pymysql,
    maxconnections=5,
    **DB_CONFIG
)

def get_db():
    return pool.connection()








