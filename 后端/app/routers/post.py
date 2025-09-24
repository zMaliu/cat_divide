from flask import Blueprint, request, g
from app.services.post_service import PostService
from app.schemas.request import PostCreateRequest, PostUpdateRequest
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService
from app.utils.security import rate_limit, validate_json
from functools import wraps
from flask import abort
import time

def rate_limit(max_requests=100, window=60, by="ip"):
    """请求频率限制装饰器"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # 获取标识符
            if by == "user":
                identifier = getattr(g, 'user_id', None)
                if identifier is None:
                    return abort(401, "未认证用户")
            elif by == "ip":
                identifier = request.remote_addr
            else:
                identifier = request.headers.get('Authorization', 'anonymous')
            
            # 存储请求时间的键
            key = f"rate_limit:{identifier}:{request.endpoint}"
            
            # 获取当前时间戳
            now = time.time()
            
            # 获取并更新请求时间列表
            if key not in g:
                g.setdefault(key, []).append(now)
            else:
                g[key].append(now)
            
            # 保留窗口期内的请求时间
            g[key] = [t for t in g[key] if t > now - window]
            
            # 检查是否超过限制
            if len(g[key]) > max_requests:
                return abort(429, "请求过于频繁，请稍后再试")
                
            return f(*args, **kwargs)
        return wrapped
    return decorator

def validate_json(f):
    """JSON请求验证装饰器"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not request.is_json:
            return abort(400, "请求必须包含JSON数据")
        return f(*args, **kwargs)
    return wrapped

post_bp = Blueprint("post", __name__)

@post_bp.before_request
def auth_middleware():
    """强制认证中间件"""
    # 排除需要认证的端点
    if request.endpoint in ["post.list_posts", "post.post_detail"]:
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
        result = PostService.get_posts(page, per_page)
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()

@post_bp.route("/<int:article_id>", methods=["GET"])
@rate_limit(max_requests=100, window=60, by="ip")  # 每个IP每分钟最多100次详情请求
def get_post_detail(article_id):
    try:
        result = PostService.get_post_detail(article_id)
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