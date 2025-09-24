from flask import Blueprint, request, g
from app.services.auth_service import AuthService
from app.schemas.response import BaseResponse
from app.utils.security import rate_limit
from app.database import get_db
import pymysql

user_bp = Blueprint("user", __name__)

@user_bp.route("/profile", methods=["GET"])
@rate_limit(max_requests=100, window=60, by="user")  # 每个用户每分钟最多查询100次个人信息
def get_user_profile():
    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401

    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401

    result = AuthService.get_user_info(user_id)
    return result.dict()

@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    """
    根据用户ID获取用户信息
    """
    try:
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT user_id, user_name, user_create_time
            FROM register 
            WHERE user_id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        if not user:
            return BaseResponse.error(404, "用户不存在").dict()
        
        return BaseResponse.success({"user": user})
    except Exception as e:
        return BaseResponse.error(500, f"获取用户信息失败: {str(e)}").dict()
    finally:
        cursor.close()
        db.close()