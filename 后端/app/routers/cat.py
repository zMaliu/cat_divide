# -*- coding: utf-8 -*-
from flask import Blueprint, request, g
from app.services.cat_service import CatService
from app.schemas.request import CatCreateRequest, CatUpdateRequest
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService
from app.utils.security import rate_limit, validate_json
import os
import uuid
import time
from werkzeug.utils import secure_filename

cat_bp = Blueprint("cat", __name__)

@cat_bp.before_request
def auth_middleware():
    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401

    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401

    g.user_id = user_id

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
# 最大文件大小5MB
MAX_CONTENT_LENGTH = 5 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@cat_bp.route("/upload-image", methods=["POST"])
@rate_limit(max_requests=20, window=60, by="user")
def upload_image():
    """
    上传原图片接口（不进行识别，只保存原图片）
    """
    try:
        # 检查文件大小
        content_length = request.content_length
        if content_length and content_length > MAX_CONTENT_LENGTH:
            return BaseResponse.error(400, "文件大小超过限制").dict(), 400

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

        # 创建上传目录
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

        # 返回原图片路径
        image_url = f"/uploads/{unique_filename}"
        return BaseResponse.success({
            "image_url": image_url,
            "filename": unique_filename
        }).dict()
            
    except RequestEntityTooLarge:
        return BaseResponse.error(400, "文件大小超过限制").dict(), 400
    except Exception as e:
        return BaseResponse.error(500, f"上传失败: {str(e)}").dict()

@cat_bp.route("/create", methods=["POST"])
@rate_limit(max_requests=10, window=60, by="user")
@validate_json
def create_cat():
    try:
        data = request.get_json()
        req = CatCreateRequest(**data)
        result = CatService.create_cat(
            req.cat_name,
            req.cat_breed,
            req.cat_age,
            req.cat_gender,
            req.cat_description,
            g.user_id,
            req.cat_image_url
        )
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"创建猫咪信息失败: {str(e)}").dict()

@cat_bp.route("/list", methods=["GET"])
@rate_limit(max_requests=100, window=60, by="ip")
def list_cats():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        result = CatService.get_cats(page, per_page)
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"获取猫咪列表失败: {str(e)}").dict()

@cat_bp.route("/<int:cat_id>", methods=["GET"])
@rate_limit(max_requests=100, window=60, by="ip")
def get_cat(cat_id):
    try:
        result = CatService.get_cat_by_id(cat_id)
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"获取猫咪信息失败: {str(e)}").dict()

@cat_bp.route("/<int:cat_id>", methods=["PUT"])
@rate_limit(max_requests=20, window=60, by="user")
@validate_json
def update_cat(cat_id):
    try:
        data = request.get_json()
        req = CatUpdateRequest(**data)
        result = CatService.update_cat(
            cat_id,
            req.cat_name,
            req.cat_breed,
            req.cat_age,
            req.cat_gender,
            req.cat_description,
            req.cat_image_url,
            g.user_id
        )
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"更新猫咪信息失败: {str(e)}").dict()

@cat_bp.route("/<int:cat_id>", methods=["DELETE"])
@rate_limit(max_requests=10, window=60, by="user")
def delete_cat(cat_id):
    try:
        result = CatService.delete_cat(cat_id, g.user_id)
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"删除猫咪信息失败: {str(e)}").dict()