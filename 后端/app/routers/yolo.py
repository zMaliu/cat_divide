# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, g, current_app, send_from_directory
from app.services.yolo_service import yolo_service
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService
import os
import uuid
import redis
import json
import time
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from app.utils.security import rate_limit

yolo_bp = Blueprint("yolo", __name__)

# Redis连接
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    # 测试连接
    redis_client.ping()
    redis_available = True
    print("Redis连接成功")
except Exception as e:
    print(f"Redis连接失败: {e}")
    redis_client = None
    redis_available = False

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
# 最大文件大小5MB
MAX_CONTENT_LENGTH = 5 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@yolo_bp.before_request
def auth_middleware():
    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401

    # 移除Bearer前缀
    if token.startswith("Bearer "):
        token = token[7:]

    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401

    g.user_id = user_id

@yolo_bp.route("/detect-cat", methods=["POST"])
@rate_limit(max_requests=10, window=60, by="user")  # 每分钟最多10次请求
def detect_cat():
    """
    猫咪检测接口
    """
    try:
        # 检查文件大小
        content_length = request.content_length
        if content_length and content_length > MAX_CONTENT_LENGTH:
            return BaseResponse.error(400, "文件大小超过限制").dict(), 400
            
        # 检查用户是否有正在处理的任务（仅在Redis可用时检查）
        if redis_available:
            user_task_key = f"user_task:{g.user_id}"
            existing_task = redis_client.get(user_task_key)
            
            if existing_task:
                return BaseResponse.error(400, "您有正在处理的任务，请稍后再试").dict(), 400

        # 检查是否有文件上传
        if 'image' not in request.files:
            return BaseResponse.error(400, "未找到图片文件").dict(), 400

        file = request.files['image']

        # 检查文件名是否为空
        if file.filename == '':
            return BaseResponse.error(400, "未选择文件").dict(), 400

        # 检查文件类型
        if not allowed_file(file.filename):
            return BaseResponse.error(400, "不支持的文件类型").dict(), 400

        # 创建上传目录 - 修正路径计算
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

        # 生成唯一文件名
        filename = secure_filename(file.filename)
        # 获取文件扩展名
        file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}_{int(time.time())}.{file_extension}"
        file_path = os.path.join(uploads_dir, unique_filename)
        
        # 保存文件
        file.save(file_path)
        
        # 验证图片文件
        try:
            from PIL import Image
            img = Image.open(file_path)
            img.verify()  # 验证图片完整性
        except Exception as e:
            # 删除无效文件
            os.remove(file_path)
            return BaseResponse.error(400, "无效的图片文件").dict(), 400

        # 检查YOLO服务是否可用
        if yolo_service is None:
            os.remove(file_path)
            return BaseResponse.error(500, "YOLO服务不可用").dict(), 500
            
        # 执行检测
        result = yolo_service.detect_with_details(file_path)
        
        # 检测完成后清理临时文件
        try:
            os.remove(file_path)
        except:
            pass
            
        return result.dict()

    except RequestEntityTooLarge:
        return BaseResponse.error(400, "文件大小超过限制").dict(), 400
    except Exception as e:
        return BaseResponse.error(500, f"检测失败: {str(e)}").dict(), 500

@yolo_bp.route("/detect-result/<task_id>", methods=["GET"])
@rate_limit(max_requests=30, window=60, by="user")  # 每分钟最多30次请求
def get_detect_result(task_id):
    """
    获取检测结果
    """
    try:
        # 从Redis获取结果（仅在Redis可用时）
        if redis_available:
            result_json = redis_client.get(f"yolo_result:{task_id}")
            if result_json:
                result = json.loads(result_json)
                
                # 清理用户任务标记
                user_task_key = f"user_task:{g.user_id}"
                redis_client.delete(user_task_key)
                
                return result
            else:
                # 任务仍在处理中
                return BaseResponse.success({
                    'status': 'processing',
                    'message': '正在处理中，请稍后查询'
                }).dict()
        else:
            # Redis不可用时返回错误
            return BaseResponse.error(500, "缓存服务不可用").dict(), 500
    except Exception as e:
        return BaseResponse.error(500, f"获取结果失败: {str(e)}").dict(), 500

@yolo_bp.route("/result-image/<filename>", methods=["GET"])
def get_result_image(filename):
    """
    获取结果图片
    """
    try:
        uploads_dir = os.path.join(current_app.root_path, "uploads")
        return send_from_directory(uploads_dir, filename)
    except Exception as e:
        return BaseResponse.error(404, "图片不存在").dict(), 404