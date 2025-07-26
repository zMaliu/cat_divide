from flask import Blueprint, request, g
from app.services.follow_service import FollowService
from app.schemas.request import FollowRequest
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService
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
def follow_user(user_id):
    return FollowService.follow_user(g.user_id, user_id).dict()
