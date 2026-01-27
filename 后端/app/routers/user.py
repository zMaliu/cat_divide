# -*- coding: utf-8 -*-
from flask import Blueprint, request, g
from app.services.auth_service import AuthService
from app.schemas.response import BaseResponse
from app.utils.security import rate_limit
from app.database import get_db
import pymysql

user_bp = Blueprint("user", __name__)

@user_bp.route("/profile", methods=["GET"])
@rate_limit(max_requests=100, window=60, by="user")  # 每用户每分钟100次请求
def get_user_profile():
    token = request.headers.get('Authorization')
    if not token:
        return BaseResponse.error(401, "未提供认证令牌").dict(), 401

    user_id = AuthService.verify_token(token)
    if not user_id:
        return BaseResponse.error(401, "无效的认证令牌").dict(), 401

    result = AuthService.get_user_info(token)
    return result.dict()

@user_bp.route("/profile", methods=["PUT"])
@rate_limit(max_requests=30, window=60, by="user")  # 每用户每分钟30次请求
def update_user_profile():
    """更新用户资料信息"""
    try:
        token = request.headers.get('Authorization')
        if not token:
            return BaseResponse.error(401, "未提供认证令牌").dict(), 401

        data = request.get_json()
        if not data:
            return BaseResponse.error(400, "请求体不能为空").dict()
        
        # 获取可选的更新字段
        user_avatar = data.get("user_avatar")
        user_bio = data.get("user_bio")
        user_location = data.get("user_location")
        user_birthday = data.get("user_birthday")
        
        # 验证生日格式（如果提供）
        if user_birthday:
            try:
                from datetime import datetime
                # 尝试解析日期格式 YYYY-MM-DD
                datetime.strptime(user_birthday, "%Y-%m-%d")
            except ValueError:
                return BaseResponse.error(400, "生日格式错误，应为 YYYY-MM-DD").dict()
        
        result = AuthService.update_user_profile(
            token=token,
            user_avatar=user_avatar,
            user_bio=user_bio,
            user_location=user_location,
            user_birthday=user_birthday
        )
        return result.dict()
    except Exception as e:
        return BaseResponse.error(500, f"更新用户信息失败: {str(e)}").dict()

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
@user_bp.route("/stats/<int:user_id>", methods=["GET"])
def get_user_stats(user_id):
    """获取用户统计数据"""
    try:
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT COUNT(*) as count FROM publish WHERE user_id = %s", (user_id,))
        post_count = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM follows WHERE followed_id = %s", (user_id,))
        follower_count = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM follows WHERE follower_id = %s", (user_id,))
        following_count = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM likes l JOIN publish p ON l.article_id = p.article_id WHERE p.user_id = %s", (user_id,))
        like_count = cursor.fetchone()['count']
        return BaseResponse.success({"post_count": post_count, "follower_count": follower_count, "following_count": following_count, "like_count": like_count}).dict()
    except Exception as e:
        return BaseResponse.error(500, f"获取统计数据失败: {str(e)}").dict()
    finally:
        cursor.close()
        db.close()

@user_bp.route("/my-stats", methods=["GET"])
@rate_limit(max_requests=100, window=60, by="user")
def get_my_stats():
    """获取当前用户的统计数据"""
    try:
        token = request.headers.get('Authorization')
        if not token:
            return BaseResponse.error(401, "未提供认证令牌").dict(), 401

        user_id = AuthService.verify_token(token)
        if not user_id:
            return BaseResponse.error(401, "无效的认证令牌").dict(), 401
        
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT COUNT(*) as count FROM publish WHERE user_id = %s", (user_id,))
        post_count = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM follows WHERE followed_id = %s", (user_id,))
        follower_count = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM follows WHERE follower_id = %s", (user_id,))
        following_count = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM likes l JOIN publish p ON l.article_id = p.article_id WHERE p.user_id = %s", (user_id,))
        like_count = cursor.fetchone()['count']
        return BaseResponse.success({
            "post_count": post_count, 
            "follower_count": follower_count, 
            "following_count": following_count, 
            "like_count": like_count
        }).dict()
    except Exception as e:
        return BaseResponse.error(500, f"获取统计数据失败: {str(e)}").dict()
    finally:
        cursor.close()
        db.close()
