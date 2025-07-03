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
        database="comments"
    )

@app.route("/api/comments",methods=["POST"])
def content():
    data=request.get_json()
    #user_id=data.get("user_id")
    content=data.get("content")
    #article_id=data.get("article_id")

    #if not content or len(content.strip())<5:
        #return jsonify({"code":400,"meg":"评论内容小于5个字"})

    db=get_db()
    cursor=db.cursor()
    try:
        cursor.execute("""
        INSERT INFO comments(content,create_time)
        VALUES(%s,NOW())
        """,(content)

                       )
        db.commit()
        return jsonify({
            "code":200,
            "meg":"评论成功",
            "comment_id":cursor.lastrowld
        })
    except Exception as e:
        db.rollback()
        return jsonify({
            "code":500,
            "msg":"评论失败"+str(e)
        })
    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)