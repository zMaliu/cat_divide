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
        database="cat"
    )

@app.route("/api/register",methods=["POST"])#定义访问路径，只接受POST请求
def register():
    data=request.get_json()
    user_name=data.get("user_name")
    password=data.get("password")


    if not user_name:
        return jsonify({"code":400,"msg":"用户名不能为空"})
    if len(password)<6:
        return jsonify({"code":400,"msg":"密码至少六位"})


    db=get_db()
    cursor=db.cursor()
    try:
        cursor.execute("SELECT * FROM  register WHERE user_name = %s",(user_name,))
        if cursor.fetchone():
            return jsonify({"code":400,"msg":"用户名已注册"})

        import hashlib
        hashed_pwd=hashlib.md5(password.encode()).hexdigest()
        cursor.execute("""
            INSERT INTO register (user_name, password,  user_create_time)
            VALUES (%s, %s, NOW())
        """, (user_name, hashed_pwd))
        db.commit()
        return jsonify({"code":200,"msg":"注册成功"})
    except Exception as e:
        db.rollback()
        return jsonify({"code":500,"msg":"服务器错误，"+str(e)})
    finally:
        cursor.close()
        db.close()

@app.route("/api/publish",methods=["POST"])#定义访问路径，只接受POST请求
def publish():
    data=request.get_json()
    user_id=data.get("user_id")
    title=data.get("title")
    content=data.get("content")

    if not user_id:
        return jsonify({"code":400,"msg":"id不存在"})
    if not title:
        return jsonify({"code":400,"msg":"标题不能为空"})
    if not content:
        return jsonify({"code":400,"msg":"内容不能为空"})


    db=get_db()
    cursor=db.cursor()
    try:
        cursor.execute("SELECT user_id FROM register WHERE user_id=%s",(user_id,))
        if not cursor.fetchone():
            return jsonify({"code":404,"msg":"用户不存在"})

        cursor.execute("""
        INSERT INTO publish (user_id,title,content,publish_time)
        VALUES (%s,%s,%s,NOW())
        """,(user_id,title,content))

        db.commit()
        return jsonify({"code":200,"msg":"发表成功"})
    except Exception as e:
        db.rollback()
        return jsonify({"code":500,"msg":"服务器错误，"+str(e)})
    finally:
        cursor.close()
        db.close()

def db_check():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        print("✅ 数据库连接成功")
        cursor.close()
        db.close()
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        exit(1)  # 启动失败时退出应用


if __name__ == '__main__':
    db_check()
    app.run(host="0.0.0.0",port=5000)