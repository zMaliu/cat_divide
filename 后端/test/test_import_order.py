# -*- coding: utf-8 -*-
# 模拟 main.py 的导入顺序

print("步骤1: 导入 load_dotenv")
from dotenv import load_dotenv

print("步骤2: 加载 .env 文件")
load_dotenv()
print(".env 文件加载完成")

print("步骤3: 导入其他模块")
from flask import Flask
from flask_cors import CORS
import os

print("步骤4: 导入 database 模块")
from app.database import get_db
print("database 模块导入完成")

print("步骤5: 测试数据库连接")
try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT 1")
    print("数据库连接成功")
    cursor.close()
    db.close()
except Exception as e:
    print(f"数据库连接失败: {str(e)}")

print("\n测试完成!")
