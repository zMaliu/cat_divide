from flask import Blueprint, request, g
from app.services.cat_service import CatService
from app.schemas.request import CatCreateRequest, CatUpdateRequest
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService
from app.utils.security import rate_limit, validate_json

cat_bp = Blueprint("cat", __name__)

@cat_bp.before_request
def auth_middleware():
    # 列表接口不需要验证
    if request.endpoint and "cat.list_cats" in request.endpoint:
        return

    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401

    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401

    g.user_id = user_id

@cat_bp.route("/create", methods=["POST"])
@rate_limit(max_requests=10, window=60, by="user")  # 每个用户每分钟最多创建10只猫咪信息
@validate_json
def create_cat():
    try:
        data = request.get_json()
        req = CatCreateRequest(**data)
        result = CatService.create_cat(
            name=req.name,
            breed=req.breed,
            age=req.age,
            gender=req.gender,
            description=req.description,
            image_url=req.image_url,  # 添加image_url参数
            owner_id=g.user_id
        )
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()

@cat_bp.route("/list", methods=["GET"])
@rate_limit(max_requests=60, window=60, by="ip")  # 每个IP每分钟最多60次列表请求
def list_cats():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        result = CatService.get_cats(page, per_page)
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()

@cat_bp.route("/<int:cat_id>", methods=["GET"])
@rate_limit(max_requests=100, window=60, by="ip")  # 每个IP每分钟最多100次详情请求
def get_cat_detail(cat_id):
    try:
        result = CatService.get_cat_detail(cat_id)
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()

@cat_bp.route("/<int:cat_id>", methods=["PUT"])
@rate_limit(max_requests=10, window=60, by="user")  # 每个用户每分钟最多修改10次猫咪信息
@validate_json
def update_cat(cat_id):
    try:
        data = request.get_json()
        req = CatUpdateRequest(**data)
        result = CatService.update_cat(
            cat_id=cat_id,
            name=req.name,
            breed=req.breed,
            age=req.age,
            gender=req.gender,
            description=req.description,
            image_url=req.image_url,  # 添加image_url参数
            owner_id=g.user_id
        )
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()

@cat_bp.route("/<int:cat_id>", methods=["DELETE"])
@rate_limit(max_requests=10, window=60, by="user")  # 每个用户每分钟最多删除10次猫咪信息
def delete_cat(cat_id):
    try:
        result = CatService.delete_cat(cat_id, g.user_id)
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()