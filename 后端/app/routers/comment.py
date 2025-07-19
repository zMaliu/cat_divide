from flask import Blueprint, request, g
from app.services.comment_service import CommentService
from app.schemas.request import CommentRequest
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService

comment_bp = Blueprint("comment", __name__)

@comment_bp.before_request
def auth_middleware():
    print(f"请求端点: {request.endpoint}")
    print(f"请求方法: {request.method}")
    print(f"请求路径: {request.path}")
    
    # 暂时移除认证检查，让所有评论API都不需要认证
    # 如果需要认证，可以在这里添加

@comment_bp.route("/create/", methods=["POST"])
def create_comment():
    data = request.get_json()
    req = CommentRequest(**data)
    # 暂时使用固定的user_id，实际项目中应该从认证中获取
    user_id = 1  # 使用xmtx的ID
    return CommentService.create_comment(
        req.article_id,
        req.article_content,
        user_id
    ).dict()

@comment_bp.route("/list/<int:article_id>", methods=["GET"])
def list_comments(article_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    return CommentService.get_comments(article_id, page, per_page).dict()
