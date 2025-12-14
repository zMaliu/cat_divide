# -*- coding: utf-8 -*-
from flask import Flask, send_from_directory, request
from flask_cors import CORS
import os
from app.routers import auth, post, comment, like, follow,chat,cat,yolo,user
from app.schemas.response import BaseResponse
from app.database import get_db
from app.utils.security import init_redis

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"], "supports_credentials": True}})

app.secret_key = os.environ.get('SECRET_KEY', 'cat123456')

# Redis配置
app.config['REDIS_HOST'] = os.environ.get('REDIS_HOST', 'localhost')
app.config['REDIS_PORT'] = int(os.environ.get('REDIS_PORT', 6379))
app.config['REDIS_DB'] = int(os.environ.get('REDIS_DB', 1))

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
app.register_blueprint(cat.cat_bp, url_prefix="/api/cat")
app.register_blueprint(yolo.yolo_bp, url_prefix="/api/yolo")
app.register_blueprint(user.user_bp, url_prefix="/api/user")

init_redis(app)

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
        print(f"收到默认图片请求: {request.method} {request.url}")
        # 使用assets目录中的默认图片
        default_img = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "default.jpg")
        
        if not os.path.exists(default_img):
            return send_from_directory(uploads_dir, "default.jpg")
        
        return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"), "default.jpg")
    except Exception as e:
        return "", 404
      
def db_check():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        print("数据库连接成功")
        cursor.close()
        db.close()
        return True
    except Exception as e:
        print(f"数据库连接失败: {str(e)}")
        return False

if __name__ == '__main__':
    ok = db_check()
    if not ok:
        print("跳过致命退出，继续启动服务")

    @app.errorhandler(Exception)
    def handle_exception(e):
        import traceback
        error_msg = str(e)
        print(f"全局异常: {error_msg}")
        print(f"异常类型: {type(e)}")
        print(f"异常详情: {traceback.format_exc()}")
        return BaseResponse.error(500, f"服务器错误：{error_msg}").dict(), 500
    
    print("启动服务器，监听端口5001...")
    # 生产环境中设置debug=False
    app.run(host="0.0.0.0", port=5001, debug=False)

