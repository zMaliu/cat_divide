from flask import Flask
from flask_cors import CORS
from app.routers import auth, post, comment,like,follow
from app.schemas.response import BaseResponse
from app.database import get_db

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = "cat123456"

# 注册蓝图
app.register_blueprint(auth.auth_bp, url_prefix='/api/auth')
app.register_blueprint(post.post_bp, url_prefix='/api/post')
app.register_blueprint(comment.comment_bp, url_prefix='/api/comment')
app.register_blueprint(like.like_bp,url_prefix="/api/like")
app.register_blueprint(follow.follow_bp, url_prefix="/api/follow")
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
        exit(1)

if __name__ == '__main__':
    db_check()

    @app.errorhandler(Exception)
    def handle_exception(e):
        return BaseResponse.error(500,f"服务器错误：{str(e)}").dict(),500
    app.run(host="0.0.0.0", port=5001)
