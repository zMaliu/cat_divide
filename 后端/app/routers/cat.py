# -*- coding: utf-8 -*-
from flask import Blueprint, request, g
from app.services.cat_service import CatService
from app.schemas.request import CatCreateRequest, CatUpdateRequest
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService
from app.utils.security import rate_limit, validate_json

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
            req.cat_image_url,
            g.user_id
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