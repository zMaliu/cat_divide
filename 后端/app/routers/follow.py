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
@rate_limit(max_requests=30, window=60, by="user")  # 每个用户每分钟最多关注30个用户
def follow_user(user_id):
    return FollowService.follow_user(g.user_id, user_id).dict()

@follow_bp.route("/<int:user_id>", methods=["DELETE"])
@rate_limit(max_requests=30, window=60, by="user")  # 每个用户每分钟最多取消关注30个用户
def unfollow_user(user_id):
    return FollowService.unfollow_user(g.user_id, user_id).dict()

@follow_bp.route("/followers/<int:user_id>", methods=["GET"])
@rate_limit(max_requests=100, window=60, by="ip")  # 每个IP每分钟最多100次粉丝列表请求
def get_followers(user_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    return FollowService.get_followers(user_id, page, per_page).dict()

@follow_bp.route("/followings/<int:user_id>", methods=["GET"])
@rate_limit(max_requests=100, window=60, by="ip")  # 每个IP每分钟最多100次关注列表请求
def get_followings(user_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    return FollowService.get_followings(user_id, page, per_page).dict()