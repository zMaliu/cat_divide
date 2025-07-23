import pymysql
from dbutils.pooled_db import PooledDB

# 数据库配置
DB_CONFIG = {
    'host': "localhost",
    'port': 3306,
    'user': "root",
    'password': "123456",
    'database': "cat",
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