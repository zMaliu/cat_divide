from flask import Blueprint, request, g
from app.services.like_service import LikeService
from app.schemas.request import LikeRequest
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService

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
def like_article(article_id):
    return LikeService.like_article(article_id, g.user_id).dict()
