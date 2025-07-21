from flask import Blueprint, request, g
from app.services.comment_service import CommentService
from app.schemas.request import CommentRequest
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService

comment_bp = Blueprint("comment", __name__)

@comment_bp.before_request
def auth_middleware():
    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401

    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401

    g.user_id = user_id

@comment_bp.route("/create", methods=["POST"])
def create_comment():
    data = request.get_json()
    req = CommentRequest(**data)
    return CommentService.create_comment(
        req.article_id,
        req.article_content,  # 注意：数据库字段名暂未修改
        g.user_id
    ).dict()

@comment_bp.route("/list/<int:article_id>", methods=["GET"])
def list_comments(article_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    return CommentService.get_comments(article_id, page, per_page).dict()
