from flask import Blueprint, request, g
from app.services.post_service import PostService
from app.schemas.request import PostRequest
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService

post_bp = Blueprint("post", __name__)

@post_bp.before_request
def auth_middleware():
    # 列表接口不需要验证
    if request.endpoint == "post.list_posts":
        return
    
    # 获取认证token
    token = request.headers.get('Authorization')
    print(f"API请求: {request.path}, 使用token: {token}")
    
    if not token:
        print(f"请求失败: {request.path}, 未提供token")
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401

    # 验证token
    user_id = AuthService.verify_token(token)
    if not user_id:
        print(f"请求失败: {request.path}, 无效token: {token}")
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401

    print(f"认证成功: 路径={request.path}, 用户ID={user_id}")
    g.user_id = user_id

@post_bp.route("/create", methods=["POST"])
def create_post():
    try:
        data = request.get_json()
        req = PostRequest(**data)
        result = PostService.create_post(req.title, req.content, g.user_id)
        print(f"创建帖子结果: 用户ID={g.user_id}, 标题={req.title}, 结果={result.dict()}")
        return result.dict()
    except Exception as e:
        print(f"创建帖子失败: {str(e)}")
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()

@post_bp.route("/list", methods=["GET"])
def list_posts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        result = PostService.get_posts(page, per_page)
        post_count = len(result.data.get("posts", [])) if result.data else 0
        print(f"获取帖子列表: 页码={page}, 每页={per_page}, 返回数量={post_count}")
        return result.dict()
    except Exception as e:
        print(f"获取帖子列表失败: {str(e)}")
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()

@post_bp.route("/detail/<int:article_id>", methods=["GET"])
def post_detail(article_id):
    try:
        result = PostService.get_post_detail(article_id)
        print(f"获取帖子详情: ID={article_id}, 状态码={result.code}")
        return result.dict()
    except Exception as e:
        print(f"获取帖子详情失败: ID={article_id}, 错误={str(e)}")
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()
