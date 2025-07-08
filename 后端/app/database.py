import pymysql

def get_db():
    return pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="cat123456",
        database="cat"
    )