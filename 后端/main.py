from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from app.routers import auth, post, comment, like, follow,chat
from app.schemas.response import BaseResponse
from app.database import get_db

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = "cat123456"

# 创建上传目录
uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
    print(f"创建上传目录: {uploads_dir}")
else:
    print(f"上传目录已存在: {uploads_dir}")

# 注册蓝图
app.register_blueprint(auth.auth_bp, url_prefix='/api/auth')
app.register_blueprint(post.post_bp, url_prefix='/api/post')
app.register_blueprint(comment.comment_bp, url_prefix='/api/comment')
app.register_blueprint(like.like_bp, url_prefix="/api/like")
app.register_blueprint(follow.follow_bp, url_prefix="/api/follow")
app.register_blueprint(chat.chat_bp, url_prefix="/api/chat")

# 静态文件服务
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """提供上传的文件"""
    try:
        return send_from_directory(uploads_dir, filename)
    except Exception as e:
        print(f"提供文件失败 {filename}: {str(e)}")
        return "", 404

@app.route('/default.jpg')
def serve_default_image():
    """提供默认图片"""
    try:
        # 使用assets目录中的默认图片
        default_img = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "default.jpg")
        if not os.path.exists(default_img):
            # 如果assets目录中没有，使用上传目录中的default.jpg
            return send_from_directory(uploads_dir, "default.jpg")
        return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"), "default.jpg")
    except Exception as e:
        print(f"提供默认图片失败: {str(e)}")
        return "", 404
      
def db_check():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        print("数据库连接成功")
        cursor.close()
        db.close()
    except Exception as e:
        print(f"数据库连接失败: {str(e)}")
        exit(1)

if __name__ == '__main__':
    db_check()

    @app.errorhandler(Exception)
    def handle_exception(e):
        print(f"全局异常: {str(e)}")
        return BaseResponse.error(500, f"服务器错误：{str(e)}").dict(), 500
    
    print("启动服务器，监听端口5001...")
    app.run(host="0.0.0.0", port=5001)
