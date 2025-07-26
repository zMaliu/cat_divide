from flask import Blueprint, request, g
from app.services.chat_service import ChatService
from app.schemas.request import MessageRequest, SessionRequest
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService

chat_bp = Blueprint("chat", __name__)

@chat_bp.before_request
def auth_middleware():
    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401

    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401

    g.user_id = user_id

@chat_bp.route("/session", methods=["POST"])
def create_session():
    """
    创建或获取会话
    """
    try:
        data = request.get_json()
        req = SessionRequest(**data)
        return ChatService.create_or_get_session(g.user_id, req.touser_id).dict()
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()

@chat_bp.route("/session", methods=["GET"])
def get_sessions():
    """
    获取会话列表
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        return ChatService.get_sessions(g.user_id, page, per_page).dict()
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()

@chat_bp.route("/message", methods=["POST"])
def send_message():
    """
    发送消息
    """
    try:
        data = request.get_json()
        req = MessageRequest(**data)
        # 先创建或获取会话
        session_result = ChatService.create_or_get_session(g.user_id, req.touser_id)
        if session_result.code != 200:
            return session_result.dict()

        session_id = session_result.data['session']['session_id']
        return ChatService.send_message(session_id, g.user_id, req.content).dict()
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()

@chat_bp.route("/message/<int:session_id>", methods=["GET"])
def get_messages(session_id):
    """
    获取会话中的消息
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        return ChatService.get_messages(session_id, g.user_id, page, per_page).dict()
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()

@chat_bp.route("/unread", methods=["GET"])
def get_unread_count():
    """
    获取未读消息数
    """
    try:
        return ChatService.get_unread_count(g.user_id).dict()
    except Exception as e:
        return BaseResponse.error(500, f"服务器错误: {str(e)}").dict()
