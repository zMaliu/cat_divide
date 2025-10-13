from flask import Blueprint, request, g
from app.services.post_service import PostService
from app.schemas.request import PostCreateRequest, PostUpdateRequest
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService
from app.utils.security import rate_limit, validate_json

post_bp = Blueprint("post", __name__)

@post_bp.before_request
def auth_middleware():
    """强制认证中间件"""
    # 排除需要认证的端点
    if request.endpoint in ["post.list_posts", "post.get_post_detail"]:
        return
    
    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401

    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401

    g.user_id = user_id

@post_bp.route("/create", methods=["POST"])
@rate_limit(max_requests=30, window=60, by="user")  # 每个用户每分钟最多发布30篇文章
@validate_json
def create_post():
    try:
        data = request.get_json()
        req = PostCreateRequest(**data)
        result = PostService.create_post(
            title=req.title,
            content=req.content,
            user_id=g.user_id
        )
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()

@post_bp.route("/list", methods=["GET"])
@rate_limit(max_requests=60, window=60, by="ip")  # 每个IP每分钟最多60次列表请求
def list_posts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 获取用户ID，如果没有认证则为None
        user_id = None
        token = request.headers.get('Authorization')
        if token:
            user_id = AuthService.verify_token(token)
            
        result = PostService.get_posts(page, per_page, user_id)
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()

@post_bp.route("/<int:article_id>", methods=["GET"])
@rate_limit(max_requests=100, window=60, by="ip")  # 每个IP每分钟最多100次详情请求
def get_post_detail(article_id):
    try:
        # 获取用户ID，如果没有认证则为None
        user_id = None
        token = request.headers.get('Authorization')
        if token:
            user_id = AuthService.verify_token(token)
            
        result = PostService.get_post_detail(article_id, user_id)
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()

@post_bp.route("/<int:article_id>", methods=["PUT"])
@rate_limit(max_requests=30, window=60, by="user")  # 每个用户每分钟最多修改30次文章
@validate_json
def update_post(article_id):
    try:
        data = request.get_json()
        req = PostUpdateRequest(**data)
        result = PostService.update_post(
            article_id=article_id,
            title=req.title,
            content=req.content,
            user_id=g.user_id
        )
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()

@post_bp.route("/<int:article_id>", methods=["DELETE"])
@rate_limit(max_requests=30, window=60, by="user")  # 每个用户每分钟最多删除30次文章
def delete_post(article_id):
    try:
        result = PostService.delete_post(article_id, g.user_id)
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()