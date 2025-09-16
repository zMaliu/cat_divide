from flask import Blueprint,request,g
from app.services.auth_service import AuthService
from app.schemas.request import PhoneLoginRequest, SendVerificationCodeRequest
from app.schemas.response import BaseResponse
from app.utils.security import rate_limit, validate_json

auth_bp=Blueprint("auth",__name__)

@auth_bp.route("/register",methods=["POST"])
@rate_limit(max_requests=5, window=300, by="ip")  # 每个IP每5分钟最多5次注册
@validate_json
def register():
    data=request.get_json()
    return AuthService.register(data["user_name"],data["password"]).dict()

@auth_bp.route("/login",methods=["POST"])
@rate_limit(max_requests=10, window=300, by="ip")  # 每个IP每5分钟最多10次登录尝试
@validate_json
def login():
    data=request.get_json()
    return AuthService.login(data["user_name"],data["password"]).dict()

@auth_bp.route("/send-code", methods=["POST"])
@rate_limit(max_requests=5, window=300, by="ip")  # 每个IP每5分钟最多发送5次验证码
@validate_json
def send_verification_code():
    """
    发送验证码接口
    """
    try:
        data = request.get_json()
        req = SendVerificationCodeRequest(**data)
        return AuthService.send_verification_code(req.phone).dict()
    except Exception as e:
        return BaseResponse.error(400, f"请求参数错误: {str(e)}").dict(), 400

@auth_bp.route("/phone-login", methods=["POST"])
@rate_limit(max_requests=10, window=300, by="ip")  # 每个IP每5分钟最多10次登录尝试
@validate_json
def phone_login():
    """
    手机号验证码登录接口
    """
    try:
        data = request.get_json()
        req = PhoneLoginRequest(**data)
        return AuthService.phone_login(req.phone, req.verification_code).dict()
    except Exception as e:
        return BaseResponse.error(400, f"请求参数错误: {str(e)}").dict(), 400

@auth_bp.route("/userinfo", methods=["GET"])
@rate_limit(max_requests=100, window=60, by="user")  # 每个用户每分钟最多100次请求
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