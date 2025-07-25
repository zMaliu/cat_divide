from flask import Blueprint,request,g
from app.services.auth_service import AuthService
from app.schemas.response import BaseResponse

auth_bp=Blueprint("auth",__name__)

@auth_bp.route("/register",methods=["POST"])
def register():
    data=request.get_json()
    return AuthService.register(data["user_name"],data["password"]).dict()

@auth_bp.route("/login",methods=["POST"])
def login():
    data=request.get_json()
    return AuthService.login(data["user_name"],data["password"]).dict()

@auth_bp.route("/userinfo", methods=["GET"])
def get_user_info():
    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401

    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401

    result = AuthService.get_user_info(user_id)
    # 打印结果以便调试
    print(f"获取用户信息结果: {result.dict()}")
    return result.dict()