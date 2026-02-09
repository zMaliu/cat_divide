# -*- coding: utf-8 -*-
from flask import Blueprint, request, g
from app.services.like_service import LikeService
from app.schemas.request import LikeRequest
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService
from app.utils.security import rate_limit

like_bp = Blueprint("like", __name__)

@like_bp.before_request
def auth_middleware():
    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401
    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401
    g.user_id = user_id

@like_bp.route("/<int:article_id>", methods=["POST"])
@rate_limit(max_requests=50, window=60, by="user")  # 每用户每分钟50次请求
def like_article(article_id):
    return LikeService.like_article(article_id, g.user_id).dict()

@like_bp.route("/<int:article_id>", methods=["DELETE"])
@rate_limit(max_requests=50, window=60, by="user")  # 每用户每分钟50次请求
def unlike_article(article_id):
    return LikeService.unlike_article(article_id, g.user_id).dict()

@like_bp.route("/my-liked", methods=["GET"])
@rate_limit(max_requests=100, window=60, by="user")  # 每用户每分钟100次请求
def get_my_liked_posts():
    """获取当前用户点赞的所有帖子"""
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
            
        result = LikeService.get_user_liked_posts(g.user_id, page, per_page)
        return result.dict()
    except ValueError:
        return BaseResponse.error(400, "页码参数错误").dict()
    except Exception as e:
        return BaseResponse.error(500, f"获取点赞帖子失败: {str(e)}").dict()