import pymysql
from dbutils.pooled_db import PooledDB

pool=PooledDB(
    creator=pymysql,
    maxconnections=5,
    host="localhost",
    port=3306,
    user="root",
    password="123456",
    database="cat"
)
def get_db():
    return pool.connection()