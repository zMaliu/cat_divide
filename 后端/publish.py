from flask import Flask,request,jsonify
import pymysql
import re
app=Flask(__name__)#创建Flask应用实例
def get_db():
    return pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="cat123456",
        database="publish"
    )

@app.route("api/publish",method=["POST"])
def publish():
    data=request.get_json()
    title=data.get("title")
    content=data.get("content")