# -*- coding: utf-8 -*-
import hashlib
import uuid
import redis
from app.database import get_db
from app.schemas.response import BaseResponse
from app.models.db_models import User
import pymysql.cursors


# Redis连接（用于存储token）
try:
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True,
        socket_connect_timeout=5
    )
    redis_client.ping()
    print("Redis token存储已连接")
except Exception as e:
    print(f"Redis连接失败: {e}")
    redis_client = None

# 全局token存储（Redis不可用时的备用方案）
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
            
            # 优先存储到Redis，7天过期
            if redis_client:
                try:
                    redis_client.setex(f"token:{token}", 7*24*3600, user_id)
                    print(f"Token已存储到Redis: {token} -> {user_id}")
                except Exception as e:
                    print(f"Redis存储失败，使用内存存储: {e}")
                    token_map[token] = user_id
            else:
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
        # 处理Bearer前缀
        if token.startswith("Bearer "):
            token = token[7:]
        
        # 从Redis或内存获取user_id
        user_id = AuthService.verify_token(token)
        if not user_id:
            return BaseResponse.error(401, "无效的认证令牌")
        
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute("""
                SELECT r.user_id, r.user_name, r.user_create_time, r.user_avatar,
                       r.user_bio, r.user_location, r.user_birthday,
                       COALESCE(us.follower_count, 0) as follower_count,
                       COALESCE(us.following_count, 0) as following_count
                FROM register r
                LEFT JOIN user_stats us ON r.user_id = us.user_id
                WHERE r.user_id = %s
            """, (user_id,))
            user = cursor.fetchone()
            if not user:
                return BaseResponse.error(404, "用户不存在")

            user_data = {
                "user_id": user["user_id"],
                "user_name": user["user_name"],
                "user_create_time": user["user_create_time"].strftime("%Y-%m-%d %H:%M:%S") if user["user_create_time"] else None,
                "user_avatar": user.get("user_avatar") or "/default.jpg",  # 头像路径，默认为 /default.jpg
                "user_bio": user.get("user_bio"),  # 个人简介
                "user_location": user.get("user_location"),  # 所在地
                "user_birthday": user["user_birthday"].strftime("%Y-%m-%d") if user.get("user_birthday") else None,  # 生日
                "follower_count": user["follower_count"],
                "following_count": user["following_count"]
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
        # 处理Bearer前缀
        if token.startswith("Bearer "):
            token = token[7:]
        
        # 从Redis删除
        if redis_client:
            try:
                deleted = redis_client.delete(f"token:{token}")
                print(f"从Redis删除token: {token}, 结果: {deleted}")
            except Exception as e:
                print(f"Redis删除失败: {e}")
        
        # 从内存删除（备用）
        if token in token_map:
            del token_map[token]
        
        return BaseResponse.success({"message": "退出成功"})

    @staticmethod
    def update_user_profile(token, user_avatar=None, user_bio=None, user_location=None, user_birthday=None):
        """更新用户资料信息"""
        # 处理Bearer前缀
        if token.startswith("Bearer "):
            token = token[7:]
        
        # 从Redis或内存获取user_id
        user_id = AuthService.verify_token(token)
        if not user_id:
            return BaseResponse.error(401, "无效的认证令牌")
        
        db = get_db()
        cursor = db.cursor()
        try:
            # 构建更新SQL，只更新提供的字段
            update_fields = []
            update_values = []
            
            if user_avatar is not None:
                update_fields.append("user_avatar = %s")
                update_values.append(user_avatar)
            
            if user_bio is not None:
                update_fields.append("user_bio = %s")
                update_values.append(user_bio)
            
            if user_location is not None:
                update_fields.append("user_location = %s")
                update_values.append(user_location)
            
            if user_birthday is not None:
                update_fields.append("user_birthday = %s")
                update_values.append(user_birthday)
            
            if not update_fields:
                return BaseResponse.error(400, "没有提供要更新的字段")
            
            # 添加user_id到更新值
            update_values.append(user_id)
            
            # 执行更新
            sql = f"""
                UPDATE register 
                SET {', '.join(update_fields)}
                WHERE user_id = %s
            """
            cursor.execute(sql, update_values)
            db.commit()
            
            return BaseResponse.success()
        except Exception as e:
            db.rollback()
            print(f"更新用户信息失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return BaseResponse.error(500, f"更新用户信息失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def verify_token(token):
        """验证token并返回用户ID"""
        original_token = token
        
        # 处理Bearer前缀
        if token.startswith("Bearer "):
            token = token[7:]
        
        # 优先从Redis获取
        user_id = None
        if redis_client:
            try:
                user_id_str = redis_client.get(f"token:{token}")
                user_id = int(user_id_str) if user_id_str else None
                print(f"从Redis验证token: token={token}, user_id={user_id}")
            except Exception as e:
                print(f"Redis读取失败，使用内存验证: {e}")
                user_id = token_map.get(token)
        else:
            user_id = token_map.get(token)
        
        print(f"验证token: 原始token={original_token}, 处理后token={token}, 结果user_id={user_id}")
        return user_id