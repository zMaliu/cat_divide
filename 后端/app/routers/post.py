# -*- coding: utf-8 -*-
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
    # 排除不需要认证的端点
    if request.endpoint in ["post.list_posts", "post.get_post_detail"]:
        return
    
    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401

    # 移除Bearer前缀
    if token.startswith("Bearer "):
        token = token[7:]

    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401

    g.user_id = user_id

@post_bp.route("/create", methods=["POST"])
@rate_limit(max_requests=30, window=60, by="user")  # 每个用户每分钟最多发布30篇文章
@validate_json
def create_post():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    if not title or not content:
        return BaseResponse.error(400, "标题与内容不能为空").dict()
    result = PostService.create_post(
        title=title,
        content=content,
        user_id=g.user_id
    )
    return result.dict()

@post_bp.route("/test", methods=["POST"])
@rate_limit(max_requests=10, window=60, by="user")
def test_post():
    return BaseResponse.success({"ok": True}).dict()

@post_bp.route("/list", methods=["GET"])
@rate_limit(max_requests=60, window=60, by="ip")  # 每个IP每分钟最多60次列表请求
def list_posts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 获取用户ID，如果用户未认证则为None
        user_id = None
        token = request.headers.get('Authorization')
        if token:
            user_id = AuthService.verify_token(token)
            
        result = PostService.get_posts(page, per_page, user_id)
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"获取文章失败: {str(e)}").dict()

@post_bp.route("/<int:article_id>", methods=["GET"])
@rate_limit(max_requests=100, window=60, by="ip")  # 每个IP每分钟最多100次详情请求
def get_post_detail(article_id):
    try:
        # 获取用户ID，如果用户未认证则为None
        user_id = None
        token = request.headers.get('Authorization')
        if token:
            user_id = AuthService.verify_token(token)
            
        result = PostService.get_post_detail(article_id, user_id)
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"获取文章失败: {str(e)}").dict()

@post_bp.route("/<int:article_id>", methods=["PUT"])
@rate_limit(max_requests=30, window=60, by="user")  # 每个用户每分钟最多30次修改
@validate_json
def update_post(article_id):
    try:
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")
        if not title or not content:
            return BaseResponse.error(400, "标题与内容不能为空").dict()
        result = PostService.update_post(
            article_id=article_id,
            title=title,
            content=content,
            user_id=g.user_id
        )
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"更新文章失败: {str(e)}").dict()

@post_bp.route("/<int:article_id>", methods=["DELETE"])
@rate_limit(max_requests=30, window=60, by="user")  # 每个用户每分钟最多30次删除
def delete_post(article_id):
    try:
        result = PostService.delete_post(article_id, g.user_id)
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"删除文章失败: {str(e)}").dict()
