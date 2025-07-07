from flask import Flask,request,jsonify,session
import pymysql
import re
from flask_cors import CORS
import hashlib

app=Flask(__name__)#创建Flask应用实例
CORS(app)
app.secret_key="cat123456"
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

@app.route("/api/login",methods=["POST"])
def login():
    data = request.get_json()
    user_name = data.get("user_name")
    password = data.get("password")

    if not user_name or not password:
        return jsonify({"code": 400, "msg": "用户名和密码不能为空"})

    db = get_db()
    cursor = db.cursor()
    try:
        # 验证用户
        cursor.execute("SELECT user_id FROM register WHERE user_name = %s", (user_name,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"code": 404, "msg": "用户不存在"})

        # 验证密码
        hashed_pwd = hashlib.md5(password.encode()).hexdigest()
        cursor.execute("SELECT password FROM register WHERE user_name = %s", (user_name,))
        db_password = cursor.fetchone()[0]

        if hashed_pwd != db_password:
            return jsonify({"code": 401, "msg": "密码错误"})

        # 登录成功，存储用户ID到session
        session['user_id'] = user[0]
        return jsonify({"code": 200, "msg": "登录成功", "user_id": user[0]})

    except Exception as e:
        return jsonify({"code": 500, "msg": "服务器错误: " + str(e)})
    finally:
        cursor.close()
        db.close()
@app.route("/api/posting",methods=["POST"])#定义访问路径，只接受POST请求
def posting():
    if "user_id" not in session:
        return jsonify({"code":401,"msg":"用户未登录"})


    data=request.get_json()
    user_id=session["user_id"]
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

@app.route("/api/comments",methods=["POST"])
def add_comments():
    if 'user_id' not in session:
        return jsonify({"code": 401, "msg": "请先登录"})

    data=request.get_json()
    article_id=data.get("article_id")
    user_id=session["user_id"]
    article_content=data.get("article_content")

    if not article_id:
        return jsonify({"code":400,"msg":"文章ID不能为空"})
    if not user_id:
        return jsonify({"code":400,"msg":"用户ID不能为空"})
    if not article_content:
        return jsonify({"code":400,"msg":"评论内容不能为空"})

    db=get_db()
    cursor=db.cursor()

    try:
        cursor.execute("SELECT article_id FROM publish WHERE article_id=%s",(article_id,))
        if not cursor.fetchone():
            return jsonify({"code":404,"msg":"文章不存在"})

        cursor.execute("SELECT user_id FROM register WHERE user_id=%s",(user_id,))
        if not cursor.fetchone():
            return jsonify({"code":404,"msg":"用户不存在"})

        cursor.execute("""
            INSERT INTO comments (article_id,user_id,article_content)
            VALUES (%s,%s,%s)
        """,(article_id,user_id,article_content))
        db.commit()
        return jsonify({"code":200,"msg":"评论成功"})

    except Exception as e:
        db.rollback()
        return jsonify({"code":500,"msg":"服务器连接错误:"+str(e)})
    finally:
        cursor.close()
        db.close()

@app.route("/api/comments/<int:article_id>",methods=["GET"])
def get_comments(article_id):
    db=get_db()
    cursor=db.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("""
        SELECT c2.*,r.user_name
        FROM comments c2 
        JOIN register r ON c2.user_id=r.user_id
        WHERE c2.article_id=%s 
        ORDER BY c2.content_time DESC
        """,(article_id,))
        comments=cursor.fetchall()
        return jsonify({"code":200,"data":comments})
    except Exception as e:
        return jsonify({"code":500,"msg":"获取评论失败："+str(e)})
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