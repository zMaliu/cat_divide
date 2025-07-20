from flask import Blueprint, request, g
from app.services.post_service import PostService
from app.schemas.request import PostRequest
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService

post_bp = Blueprint("post", __name__)

@post_bp.before_request
def auth_middleware():
    if request.endpoint in ["post.list_posts", "post.search_posts"]:
        return

    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401

    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401

    g.user_id = user_id

@post_bp.route("/create", methods=["POST"])
def create_post():
    data = request.get_json()
    req = PostRequest(**data)
    return PostService.create_post(
        req.title,
        req.content,
        g.user_id
    ).dict()

@post_bp.route("/list", methods=["GET"])
def list_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    return PostService.get_posts(page, per_page).dict()

@post_bp.route("/search", methods=["GET"])
def search_posts():
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    return PostService.search_posts(keyword, page, per_page).dict()

@post_bp.route("/detail/<int:article_id>", methods=["GET"])
def post_detail(article_id):
    return PostService.get_post_detail(article_id).dict()
