from flask import Blueprint, request, g
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService
from app.services.cat_service import CatService
from app.services.vector_service import VectorService
from werkzeug.utils import secure_filename
import os
import time
import logging

logger = logging.getLogger(__name__)
vector_bp = Blueprint('vector', __name__, url_prefix='/api/vector')


@vector_bp.before_request
def auth_middleware():
    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401

    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401

    g.user_id = user_id


@vector_bp.route('/extract', methods=['POST'])
def extract_features():
    try:
        if 'image' not in request.files or not request.files['image'].filename:
            return BaseResponse.error(400, "未选择图像文件").dict(), 400

        image = request.files['image']
        upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uploads")
        os.makedirs(upload_dir, exist_ok=True)

        # 保存临时文件
        filename = f"temp_{int(time.time())}_{secure_filename(image.filename)}"
        filepath = os.path.join(upload_dir, filename)
        image.save(filepath)

        try:
            # TODO: 完善特征提取方法
            vector = VectorService.extract_features(filepath)
            return BaseResponse.success(data={"vector": vector}).dict()
        finally:
            # 删除临时文件
            if os.path.exists(filepath):
                os.remove(filepath)

    except Exception as e:
        logger.error(f"Extract features error: {str(e)}")
        return BaseResponse.error(500, "特征提取失败").dict(), 500


@vector_bp.route('/search', methods=['POST'])
def search_similar_cats():
    try:
        data = request.get_json()
        vector = data.get('vector')
        threshold = data.get('threshold', 0.7)
        top_k = data.get('top_k', 5)

        if not vector:
            return BaseResponse.error(400, "缺少向量数据").dict(), 400

        results = VectorService.search_similar_cats(vector, threshold, top_k)
        return BaseResponse.success(data={"results": results}).dict()

    except Exception as e:
        logger.error(f"Search similar cats error: {str(e)}")
        return BaseResponse.error(500, "搜索相似猫咪失败").dict(), 500


@vector_bp.route('/cat/<cat_id>', methods=['POST'])
def add_cat_vector(cat_id):
    if 'image' not in request.files or not request.files['image'].filename:
        return BaseResponse.error(400, "缺少图像文件").dict(), 400

    image = request.files['image']
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # 保存临时文件
    filename = secure_filename(image.filename)
    filepath = os.path.join(upload_dir, filename)
    image.save(filepath)

    try:
        # 检查猫咪是否存在且属于当前用户
        result = CatService.get_cat_by_id(cat_id)
        if result.code != 200:
            return BaseResponse.error(400, "猫咪不存在").dict(), 400

        cat = result.data['cat']
        if cat['owner_id'] != g.id:
            return BaseResponse.error(403, "无权访问该猫咪").dict(), 403

        # 添加向量
        if VectorService.add_cat_vector(cat_id, g.user_id, filepath):
            return BaseResponse.success(message="特征向量添加成功").dict()
        else:
            return BaseResponse.error(500, "特征向量添加失败").dict(), 500
    finally:
        # 删除临时文件
        if os.path.exists(filepath):
            os.remove(filepath)
