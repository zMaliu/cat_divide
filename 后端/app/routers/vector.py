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


@vector_bp.route('/search', methods=['POST'])
def search_by_image():
    """
    以图搜猫：上传图片 → 提取向量 → Milvus检索 → 返回相似猫咪档案
    """
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
            # 提取向量
            vector = VectorService.extract_features(filepath)

            if not vector:
                return BaseResponse.error(400, "缺少向量数据").dict(), 400

            data = request.get_json()
            threshold = data.get('threshold', 0.7)
            top_k = data.get('top_k', 5)

            # Milvus检索
            milvus_results = VectorService.search_similar_cats(vector, threshold, top_k)

            if len(milvus_results) == 0 :
                # 找不到相似的猫,返回信息给前端,让用户对猫咪进行基本描述(描述后直接存入猫咪档案，设置状态为未审核)
                return BaseResponse.error(501, "未找到相似的猫，请让用户对猫咪进行基本描述").dict(), 501

            # 找到相似的猫，返回相似的猫信息给前端
            return BaseResponse.success(data={"milvus_results": milvus_results}).dict()

        finally:
            # 删除临时文件
            if os.path.exists(filepath):
                os.remove(filepath)
    except Exception as e:
        logger.error(f"识别猫咪失败: {str(e)}")
        return BaseResponse.error(500, "识别猫咪失败").dict(), 500


@vector_bp.route('/cat/<cat_id>', methods=['POST'])
def add_cat_vector(cat_id):
    """
        为已有猫咪档案绑定向量（生成向量存入Milvus）
        在猫咪档案中审核修改猫咪信息，正确无误后为该猫咪绑定向量
        前提：档案已通过前端上传了图片（image_url存在）
        操作：读取该图片→提取向量→存入Milvus→更新档案状态
        注意：此接口不接收文件上传！
    """
    try:
        # 检查猫咪是否存在且属于当前用户
        result = CatService.get_cat_by_id(cat_id)
        if result.code != 200:
            return BaseResponse.error(400, "猫咪不存在").dict(), 400

        cat = result.data['cat']
        if cat['owner_id'] != g.user_id:
            return BaseResponse.error(403, "无权访问该猫咪").dict(), 403

        filepath = cat['image_url']

        # 添加向量
        if VectorService.add_cat_vector(cat_id, g.user_id, filepath):
            return BaseResponse.success(message="特征向量添加成功").dict()
        else:
            return BaseResponse.error(500, "特征向量添加失败").dict(), 500

    except Exception as e:
        logger.error(f"为猫咪绑定向量失败: {str(e)}")
        return BaseResponse.error(500, "为猫咪绑定向量失败").dict(), 500
