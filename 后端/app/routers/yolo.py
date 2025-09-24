from flask import Blueprint, request, jsonify, g
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

# 初始化Redis连接
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# 最大文件大小 5MB
MAX_CONTENT_LENGTH = 5 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@yolo_bp.before_request
def auth_middleware():
    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401

    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401

    g.user_id = user_id

@yolo_bp.route("/detect-cat", methods=["POST"])
@rate_limit(max_requests=10, window=60, by="user")  # 每个用户每分钟最多10次图像识别请求
def detect_cat():
    """
    接收上传的猫咪图片并返回检测结果
    """
    try:
        # 检查内容长度
        content_length = request.content_length
        if content_length and content_length > MAX_CONTENT_LENGTH:
            return BaseResponse.error(400, "文件过大").dict(), 400
            
        # 检查该用户是否已经有正在处理的任务
        user_task_key = f"user_task:{g.user_id}"
        existing_task = redis_client.get(user_task_key)
        
        if existing_task:
            return BaseResponse.error(400, "您有任务正在处理中，请等待完成后再提交新任务").dict(), 400

        # 检查是否有文件上传
        if 'image' not in request.files:
            return BaseResponse.error(400, "未提供图片文件").dict(), 400

        file = request.files['image']

        # 检查文件名
        if file.filename == '':
            return BaseResponse.error(400, "未选择文件").dict(), 400

        # 检查文件类型
        if not allowed_file(file.filename):
            return BaseResponse.error(400, "不支持的文件类型").dict(), 400

        # 保存上传的文件
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

        # 使用安全的文件名
        filename = secure_filename(file.filename)
        # 生成唯一文件名
        file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}_{int(time.time())}.{file_extension}"
        file_path = os.path.join(uploads_dir, unique_filename)
        
        # 保存文件
        file.save(file_path)
        
        # 验证文件是否为有效图片
        try:
            from PIL import Image
            img = Image.open(file_path)
            img.verify()  # 验证图片完整性
        except Exception as e:
            # 删除无效文件
            os.remove(file_path)
            return BaseResponse.error(400, "文件不是有效的图片").dict(), 400

        # 为该用户设置任务标记，防止重复提交 (设置60秒过期时间)
        task_id = str(uuid.uuid4())
        task_data = {
            'file_path': file_path,
            'task_id': task_id,
            'user_id': g.user_id,
            'status': 'pending'
        }
        
        redis_client.setex(user_task_key, 60, task_id)
        # 将任务放入消息队列
        redis_client.lpush('yolo_tasks', json.dumps(task_data))
        
        # 立即返回任务ID，客户端可以通过任务ID查询结果
        return BaseResponse.success({
            'task_id': task_data['task_id'],
            'message': '任务已提交，正在处理中'
        }).dict()

    except RequestEntityTooLarge:
        return BaseResponse.error(400, "文件过大").dict(), 400
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict(), 500

@yolo_bp.route("/detect-result/<task_id>", methods=["GET"])
@rate_limit(max_requests=30, window=60, by="user")  # 每个用户每分钟最多30次结果查询请求
def get_detect_result(task_id):
    """
    获取图像识别任务结果
    """
    try:
        # 检查任务是否属于当前用户
        result_json = redis_client.get(f"yolo_result:{task_id}")
        if result_json:
            result = json.loads(result_json)
            
            # 清除用户任务标记
            user_task_key = f"user_task:{g.user_id}"
            redis_client.delete(user_task_key)
            
            return result
        else:
            # 检查任务是否仍在处理队列中
            return BaseResponse.success({
                'status': 'processing',
                'message': '任务仍在处理中，请稍后再查询'
            }).dict()
    except Exception as e:
        return BaseResponse.error(500, f"查询结果失败: {str(e)}").dict(), 500