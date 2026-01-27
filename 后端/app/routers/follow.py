# -*- coding: utf-8 -*-
from flask import Blueprint, request, g
from app.services.follow_service import FollowService
from app.schemas.request import FollowRequest
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService
from app.utils.security import rate_limit

follow_bp = Blueprint("follow", __name__)

@follow_bp.before_request
def auth_middleware():
    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401
    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401
    g.user_id = user_id

@follow_bp.route("/<int:user_id>", methods=["POST"])
@rate_limit(max_requests=50, window=60, by="user")
def follow_user(user_id):
    return FollowService.follow_user(g.user_id, user_id).dict()

@follow_bp.route("/<int:user_id>", methods=["DELETE"])
@rate_limit(max_requests=50, window=60, by="user")
def unfollow_user(user_id):
    return FollowService.unfollow_user(g.user_id, user_id).dict()

@follow_bp.route("/my-followers", methods=["GET"])
@rate_limit(max_requests=100, window=60, by="user")
def get_my_followers():
    """获取当前用户的粉丝列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # 限制每页数量
        if per_page > 100:
            per_page = 100
        if per_page < 1:
            per_page = 20
        if page < 1:
            page = 1
            
        return FollowService.get_followers(g.user_id, page, per_page, g.user_id).dict()
    except ValueError:
        return BaseResponse.error(400, "页码参数错误").dict()
    except Exception as e:
        return BaseResponse.error(500, f"获取粉丝列表失败: {str(e)}").dict()

@follow_bp.route("/my-followings", methods=["GET"])
@rate_limit(max_requests=100, window=60, by="user")
def get_my_followings():
    """获取当前用户的关注列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # 限制每页数量
        if per_page > 100:
            per_page = 100
        if per_page < 1:
            per_page = 20
        if page < 1:
            page = 1
            
        return FollowService.get_followings(g.user_id, page, per_page).dict()
    except ValueError:
        return BaseResponse.error(400, "页码参数错误").dict()
    except Exception as e:
        return BaseResponse.error(500, f"获取关注列表失败: {str(e)}").dict()