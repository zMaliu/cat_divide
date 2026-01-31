# -*- coding: utf-8 -*-
from flask import Blueprint, request, g
from app.services.favorite_service import FavoriteService
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService
from app.utils.security import rate_limit

favorite_bp = Blueprint("favorite", __name__)

@favorite_bp.before_request
def auth_middleware():
    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401
    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401
    g.user_id = user_id

@favorite_bp.route("/<int:article_id>", methods=["POST"])
@rate_limit(max_requests=50, window=60, by="user")  # 每用户每分钟50次请求
def favorite_article(article_id):
    """收藏帖子"""
    return FavoriteService.favorite_article(article_id, g.user_id).dict()

@favorite_bp.route("/<int:article_id>", methods=["DELETE"])
@rate_limit(max_requests=50, window=60, by="user")  # 每用户每分钟50次请求
def unfavorite_article(article_id):
    """取消收藏"""
    return FavoriteService.unfavorite_article(article_id, g.user_id).dict()

@favorite_bp.route("/my-favorites", methods=["GET"])
@rate_limit(max_requests=100, window=60, by="user")  # 每用户每分钟100次请求
def get_my_favorite_posts():
    """获取当前用户收藏的所有帖子"""
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
            
        result = FavoriteService.get_user_favorite_posts(g.user_id, page, per_page)
        return result.dict()
    except ValueError:
        return BaseResponse.error(400, "页码参数错误").dict()
    except Exception as e:
        return BaseResponse.error(500, f"获取收藏帖子失败: {str(e)}").dict()
