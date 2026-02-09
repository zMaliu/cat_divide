# -*- coding: utf-8 -*-
# 模拟 main.py 的完整导入顺序

print("步骤1: 导入 load_dotenv")
from dotenv import load_dotenv

print("步骤2: 加载 .env 文件")
load_dotenv()
print(".env 文件加载完成")

print("步骤3: 导入 Flask 相关模块")
from flask import Flask, send_from_directory, request
from flask_cors import CORS
import os

print("步骤4: 导入 database 模块")
from app.database import get_db
print("database 模块导入完成")

print("步骤5: 导入路由模块")
try:
    print("  导入 auth 路由...")
    from app.routers import auth
    print("  auth 路由导入成功")
    
    print("  导入 post 路由...")
    from app.routers import post
    print("  post 路由导入成功")
    
    print("  导入 comment 路由...")
    from app.routers import comment
    print("  comment 路由导入成功")
    
    print("  导入 like 路由...")
    from app.routers import like
    print("  like 路由导入成功")
    
    print("  导入 favorite 路由...")
    from app.routers import favorite
    print("  favorite 路由导入成功")
    
    print("  导入 follow 路由...")
    from app.routers import follow
    print("  follow 路由导入成功")
    
    print("  导入 chat 路由...")
    from app.routers import chat
    print("  chat 路由导入成功")
    
    print("  导入 cat 路由...")
    from app.routers import cat
    print("  cat 路由导入成功")
    
    print("  导入 yolo 路由...")
    from app.routers import yolo
    print("  yolo 路由导入成功")
    
    print("  导入 user 路由...")
    from app.routers import user
    print("  user 路由导入成功")
    
    print("  导入 vector 路由...")
    from app.routers import vector
    print("  vector 路由导入成功")
    
    print("所有路由模块导入成功!")
except Exception as e:
    print(f"路由模块导入失败: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n步骤6: 测试数据库连接")
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
