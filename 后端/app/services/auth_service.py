# -*- coding: utf-8 -*-
import hashlib
import uuid
from app.database import get_db
from app.schemas.response import BaseResponse
from app.models.db_models import User
import pymysql.cursors

# 全局token存储
token_map = {}

class AuthService:
    @staticmethod
    def register(user_name, password):
        if not user_name:
            return BaseResponse.error(400, "用户名不能为空")
        if len(password) < 6:
            return BaseResponse.error(400, "密码至少6位")

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("SELECT * FROM register WHERE user_name = %s", (user_name,))
            if cursor.fetchone():
                return BaseResponse.error(400, "用户已注册")

            hashed_pwd = hashlib.md5(password.encode()).hexdigest()
            cursor.execute("""
                INSERT INTO register (user_name, password, user_create_time)
                VALUES (%s, %s, NOW())
            """, (user_name, hashed_pwd))
            db.commit()
            return BaseResponse.success()
        except Exception as e:
            db.rollback()
            print(f"注册失败: {str(e)}")
            return BaseResponse.error(500, f"服务器错误: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def login(user_name, password):
        print(f"登录请求: user_name={user_name}, password={password}")
        
        if not user_name or not password:
            return BaseResponse.error(400, "用户名和密码不能为空")

        db = get_db()
        cursor = db.cursor()
        try:
            print(f"执行数据库查询: SELECT user_id, password FROM register WHERE user_name = '{user_name}'")
            cursor.execute("SELECT user_id, password FROM register WHERE user_name = %s", (user_name,))
            user = cursor.fetchone()
            print(f"查询结果: {user}")
            print(f"查询结果类型: {type(user)}")
            
            if not user:
                return BaseResponse.error(400, "用户不存在")

            print(f"用户数据: {user}")
            hashed_pwd = hashlib.md5(password.encode()).hexdigest()
            print(f"输入密码哈希: {hashed_pwd}")
            print(f"数据库密码: {user['password'] if isinstance(user, dict) else user[1]}")
            
            # 兼容处理，支持字典和元组两种格式
            if isinstance(user, dict):
                db_password = user["password"]
                user_id = user["user_id"]
            else:
                db_password = user[1]
                user_id = user[0]
            
            if db_password != hashed_pwd:
                return BaseResponse.error(400, "密码错误")

            # 生成token
            token = str(uuid.uuid4())
            token_map[token] = user_id
            
            return BaseResponse.success(data={"token": token, "user_id": user_id})
        except Exception as e:
            print(f"登录异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return BaseResponse.error(500, f"服务器错误: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_user_info(token):
        if token not in token_map:
            return BaseResponse.error(401, "无效的认证令牌")
        
        user_id = token_map[token]
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT user_id, user_name, user_create_time, user_avatar, user_bio, 
                       user_location, user_website, user_birthday
                FROM register 
                WHERE user_id = %s
            """, (user_id,))
            user = cursor.fetchone()
            if not user:
                return BaseResponse.error(404, "用户不存在")

            user_data = {
                "user_id": user[0],
                "user_name": user[1],
                "user_create_time": user[2].strftime("%Y-%m-%d %H:%M:%S") if user[2] else None,
                "user_avatar": user[3],
                "user_bio": user[4],
                "user_location": user[5],
                "user_website": user[6],
                "user_birthday": user[7].strftime("%Y-%m-%d") if user[7] else None
            }
            return BaseResponse.success(data=user_data)
        except Exception as e:
            print(f"获取用户信息失败: {str(e)}")
            return BaseResponse.error(500, f"服务器错误: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def logout(token):
        if token in token_map:
            del token_map[token]
            return BaseResponse.success(message="退出成功")
        return BaseResponse.error(401, "无效的认证令牌")

    @staticmethod
    def verify_token(token):
        """验证token并返回用户ID"""
        print(f"验证token: {token}")
        print(f"当前token_map: {token_map}")
        result = token_map.get(token)
        print(f"验证结果: {result}")
        return result

