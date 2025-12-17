# -*- coding: utf-8 -*-
from flask import Blueprint,request,g
from app.services.auth_service import AuthService
from app.schemas.response import BaseResponse
from app.utils.security import rate_limit, validate_json

auth_bp=Blueprint("auth",__name__)

@auth_bp.route("/register",methods=["POST"])
@rate_limit(max_requests=5, window=300, by="ip")  # 每个IP每5分钟最多5次注册
def register():
    try:
        print(f"收到注册请求: {request.method} {request.url}")
        data = request.get_json()
        print(f"注册数据: {data}")
        
        if not data:
            print("错误: 没有收到JSON数据")
            return BaseResponse.error(400, "请求数据格式错误").dict()
        
        if "user_name" not in data or "password" not in data:
            print("错误: 缺少必要字段")
            return BaseResponse.error(400, "用户名和密码不能为空").dict()
        
        result = AuthService.register(data["user_name"], data["password"])
        print(f"注册结果: {result}")
        return result.dict()
    except Exception as e:
        print(f"注册路由异常: {str(e)}")
        return BaseResponse.error(500, f"注册失败: {str(e)}").dict()

@auth_bp.route("/login",methods=["POST"])
@rate_limit(max_requests=10, window=60, by="ip")  # 每个IP每分钟最多10次
def login():
    try:
        print(f"收到登录请求: {request.method} {request.url}")
        data = request.get_json()
        print(f"请求数据: {data}")
        
        if not data:
            print("错误: 没有收到JSON数据")
            return BaseResponse.error(400, "请求数据格式错误").dict()
        
        if "user_name" not in data or "password" not in data:
            print("错误: 缺少必要字段")
            return BaseResponse.error(400, "用户名和密码不能为空").dict()
        
        result = AuthService.login(data["user_name"], data["password"])
        print(f"登录结果: {result}")
        return result.dict()
    except Exception as e:
        print(f"登录路由异常: {str(e)}")
        return BaseResponse.error(500, f"登录失败: {str(e)}").dict()

@auth_bp.route("/get_user_info",methods=["GET"])
@rate_limit(max_requests=100, window=60, by="user")  # 每个用户每分钟最多100次
def get_user_info():
    # 从请求头获取token
    token = request.headers.get("Authorization")
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict()
    
    # 移除Bearer前缀
    if token.startswith("Bearer "):
        token = token[7:]
    
    result = AuthService.get_user_info(token)
    return result.dict()

@auth_bp.route("/logout",methods=["POST"])
def logout():
    # 从请求头获取token
    token = request.headers.get("Authorization")
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict()
    
    # 移除Bearer前缀
    if token.startswith("Bearer "):
        token = token[7:]
    
    result = AuthService.logout(token)
    return result.dict()