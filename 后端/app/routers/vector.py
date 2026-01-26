from flask import Blueprint, request, jsonify
from app.services.auth_service import login_required
from app.schemas.response import BaseResponse
from app.services.vector_service import VectorService
from werkzeug.utils import secure_filename
import os
import time
import logging

logger = logging.getLogger(__name__)
vector_bp = Blueprint('vector', __name__, url_prefix='/api/vector')

@vector_bp.route('/extract', methods=['POST'])
@login_required
def extract_features(current_user):
    try:
        if 'image' not in request.files:
            return BaseResponse.error(400, "缺少图像文件")
        
        image = request.files['image']
        upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存临时文件
        filename = f"temp_{int(time.time())}_{secure_filename(image.filename)}"
        filepath = os.path.join(upload_dir, filename)
        image.save(filepath)
        
        try:
            vector = VectorService.extract_features(filepath)
            return BaseResponse.success(data={"vector": vector})
        finally:
            # 删除临时文件
            if os.path.exists(filepath):
                os.remove(filepath)
                
    except Exception as e:
        logger.error(f"Extract features error: {str(e)}")
        return BaseResponse.error(500, "特征提取失败")

@vector_bp.route('/search', methods=['POST'])
@login_required
def search_similar_cats(current_user):
    try:
        data = request.json
        vector = data.get('vector')
        threshold = data.get('threshold', 0.7)
        top_k = data.get('top_k', 5)
        
        if not vector:
            return BaseResponse.error(400, "缺少向量数据")
        
        results = VectorService.search_similar_cats(vector, threshold, top_k)
        return BaseResponse.success(data={"results": results})
        
    except Exception as e:
        logger.error(f"Search similar cats error: {str(e)}")
        return BaseResponse.error(500, "搜索相似猫咪失败")

@vector_bp.route('/cat/<cat_id>', methods=['POST'])
@login_required
def add_cat_vector(current_user, cat_id):
    try:
        if 'image' not in request.files:
            return BaseResponse.error(400, "缺少图像文件")
        
        image = request.files['image']
        upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存临时文件
        filename = secure_filename(image.filename)
        filepath = os.path.join(upload_dir, filename)
        image.save(filepath)
        
        try:
            # 检查猫咪是否存在且属于当前用户
            cat = CatService.get_cat_by_id(cat_id)
            if not cat or cat.user_id != current_user.id:
                return BaseResponse.error(403, "无权访问该猫咪")
            
            # 添加向量
            if VectorService.add_cat_vector(cat_id, current_user.id, filepath):
                return BaseResponse.success(message="特征向量添加成功")
            else:
                return BaseResponse.error(500, "特征向量添加失败")
        finally:
            # 删除临时文件
            if os.path.exists(filepath):
                os.remove(filepath)
                
    except Exception as e:
        logger.error(f"Add cat vector error: {str(e)}")
        return BaseResponse.error(500, "添加特征向量失败")