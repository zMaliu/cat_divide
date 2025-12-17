# -*- coding: utf-8 -*-
from flask import Blueprint, request, g, jsonify
from app.services.chat_service import ChatService
from app.schemas.request import MessageRequest, SessionRequest
from app.schemas.response import BaseResponse
from app.services.auth_service import AuthService
from app.utils.security import rate_limit, validate_json

chat_bp = Blueprint("chat", __name__)

@chat_bp.before_request
def auth_middleware():
    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401

    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "认证令牌无效").dict(), 401

    g.user_id = user_id

@chat_bp.route("/send", methods=["POST"])
@rate_limit(max_requests=30, window=60, by="user")  # 每分钟30次
@validate_json
def send_message():
    try:
        data = request.get_json()
        if not data or not isinstance(data, dict):
            return BaseResponse.error(400, "无效的JSON数据").dict()
        req = MessageRequest(**data)
        # 创建或获取会话
        session_result = ChatService.create_or_get_session(g.user_id, req.to_user_id)
        if session_result.code != 200:
            return session_result.dict()

        session_id = session_result.data['session']['session_id']
        result = ChatService.send_message(
            session_id=session_id,
            fromuser_id=g.user_id,
            content=req.content
        )
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"发送消息失败: {str(e)}").dict()

@chat_bp.route("/messages/<int:to_user_id>", methods=["GET"])
@rate_limit(max_requests=60, window=60, by="user")  # 每分钟60次
def get_messages(to_user_id):
    try:
        # 创建或获取会话
        session_result = ChatService.create_or_get_session(g.user_id, to_user_id)
        if session_result.code != 200:
            return session_result.dict()

        session_id = session_result.data['session']['session_id']
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        result = ChatService.get_messages(session_id, g.user_id, page, per_page)
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"获取消息失败: {str(e)}").dict()

@chat_bp.route("/sessions", methods=["GET"])
@rate_limit(max_requests=60, window=60, by="user")  # 每分钟60次
def get_chat_sessions():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        result = ChatService.get_sessions(g.user_id, page, per_page)
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"获取会话列表失败: {str(e)}").dict()

@chat_bp.route("/session", methods=["POST", "GET"])
def session_handler():
    """
    会话处理器
    GET: 获取会话列表
    POST: 创建或获取会话
    """
    try:
        if request.method == "GET":
            # GET请求获取会话列表
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            return ChatService.get_sessions(g.user_id, page, per_page).dict()
        
        elif request.method == "POST":
            # POST请求创建会话
            if not request.is_json:
                return BaseResponse.error(400, "请求必须是JSON格式").dict()
            
            data = request.get_json()
            if not data or not isinstance(data, dict):
                return BaseResponse.error(400, "无效的JSON数据").dict()
            req = SessionRequest(**data)
            return ChatService.create_or_get_session(g.user_id, req.touser_id).dict()
            
    except Exception as e:
        return BaseResponse.error(500, f"会话处理失败: {str(e)}").dict()

@chat_bp.route("/message", methods=["POST"])
@validate_json
def send_new_message():
    """
    发送新消息
    """
    try:
        data = request.get_json()
        if not data or not isinstance(data, dict):
            return BaseResponse.error(400, "无效的JSON数据").dict()
        req = MessageRequest(**data)
        # 创建或获取会话
        session_result = ChatService.create_or_get_session(g.user_id, req.touser_id)
        if session_result.code != 200:
            return session_result.dict()

        session_id = session_result.data['session']['session_id']
        return ChatService.send_message(session_id, g.user_id, req.content).dict()
    except Exception as e:
        return BaseResponse.error(500, f"发送消息失败: {str(e)}").dict()

@chat_bp.route("/message/<int:session_id>", methods=["GET"])
def get_session_messages(session_id):
    """
    获取指定会话的消息
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        return ChatService.get_messages(session_id, g.user_id, page, per_page).dict()
    except Exception as e:
        return BaseResponse.error(500, f"获取消息失败: {str(e)}").dict()

@chat_bp.route("/unread", methods=["GET"])
def get_unread_count():
    """
    获取未读消息数量
    """
    try:
        return ChatService.get_unread_count(g.user_id).dict()
    except Exception as e:
        return BaseResponse.error(500, f"获取未读消息数量失败: {str(e)}").dict()