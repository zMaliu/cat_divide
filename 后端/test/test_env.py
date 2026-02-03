# -*- coding: utf-8 -*-
from dotenv import load_dotenv
import os

# 加载 .env文件配置
print("开始加载 .env 文件...")
load_dotenv()
print(".env 文件加载完成")

# 打印环境变量
print("环境变量:")
print(f"DB_HOST: {os.environ.get('DB_HOST')}")
print(f"DB_PORT: {os.environ.get('DB_PORT')}")
print(f"DB_USER: {os.environ.get('DB_USER')}")
print(f"DB_PASSWORD: {os.environ.get('DB_PASSWORD')}")
print(f"DB_NAME: {os.environ.get('DB_NAME')}")

# 测试数据库连接
print("\n测试数据库连接...")
try:
    import pymysql
    conn = pymysql.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=int(os.environ.get('DB_PORT', 3306)),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'root'),
        database=os.environ.get('DB_NAME', 'cat'),
        charset="utf8mb4"
    )
    print("数据库连接成功!")
    conn.close()
except Exception as e:
    print(f"数据库连接失败: {str(e)}")

# 测试Redis连接
print("\n测试Redis连接...")
try:
    import redis
    r = redis.Redis(
        host=os.environ.get('REDIS_HOST', 'localhost'),
        port=int(os.environ.get('REDIS_PORT', 6379)),
        db=int(os.environ.get('REDIS_DB', 1)),
        decode_responses=True
    )
    r.ping()
    print("Redis连接成功!")
except Exception as e:
    print(f"Redis连接失败: {str(e)}")

print("\n测试完成!")
