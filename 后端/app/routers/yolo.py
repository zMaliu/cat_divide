
from flask import Blueprint, request, jsonify
from app.services.yolo_service import yolo_service
from app.schemas.response import BaseResponse
import os
import uuid

yolo_bp = Blueprint("yolo", __name__)

@yolo_bp.route("/detect-cat", methods=["POST"])
def detect_cat():
    """
    接收上传的猫咪图片并返回检测结果
    """
    try:
        # 检查是否有文件上传
        if 'image' not in request.files:
            return BaseResponse.error(400, "未提供图片文件").dict(), 400

        file = request.files['image']

        # 检查文件名
        if file.filename == '':
            return BaseResponse.error(400, "未选择文件").dict(), 400

        # 保存上传的文件
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

        # 生成唯一文件名
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(uploads_dir, filename)
        file.save(file_path)

        # 使用YOLO进行检测
        if yolo_service is None:
            return BaseResponse.error(500, "YOLO模型未正确加载").dict(), 500

        result = yolo_service.detect_cat_in_image(file_path)

        #删除上传的文件以节省空间
        os.remove(file_path)

        return result.dict()

    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict(), 500
