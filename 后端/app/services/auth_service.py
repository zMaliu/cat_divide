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
            return BaseResponse.error(400, "密码至少六位")

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("SELECT * FROM register WHERE user_name = %s", (user_name,))
            if cursor.fetchone():
                return BaseResponse.error(400, "用户名已注册")

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
        if not user_name or not password:
            return BaseResponse.error(400, "用户名和密码不能为空")

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("SELECT user_id, password FROM register WHERE user_name = %s", (user_name,))
            user = cursor.fetchone()
            if not user:
                return BaseResponse.error(404, "用户不存在")

            user_id = user['user_id'] if isinstance(user, dict) else user[0]
            db_password = user['password'] if isinstance(user, dict) else user[1]
            hashed_pwd = hashlib.md5(password.encode()).hexdigest()

            if hashed_pwd != db_password:
                return BaseResponse.error(401, "密码错误")

            # 生成token并存储
            token = str(uuid.uuid4())
            token_map[token] = user_id
            print(f"登录成功: 用户ID={user_id}, token={token}")
            return BaseResponse.success({"user_id": user_id, "token": token})
        except Exception as e:
            print(f"登录失败: {str(e)}")
            return BaseResponse.error(500, f"服务器错误: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def verify_token(token):
        original_token = token
        
        # 处理Bearer前缀
        if token.startswith("Bearer "):
            token = token[7:]
        
        user_id = token_map.get(token)
        print(f"验证token: 原始token={original_token}, 处理后token={token}, 结果user_id={user_id}")
        return user_id
    
    @staticmethod
    def get_user_info(user_id):
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            # 首先检查表结构
            cursor.execute("DESCRIBE register")
            columns = {row['Field']: True for row in cursor.fetchall()}
            print(f"数据库表结构: {columns}")
            
            # 构建查询，只包含存在的列
            query = "SELECT user_id, user_name, user_create_time"
            
            if 'like_count' in columns:
                query += ", like_count"
            
            if 'follower_count' in columns:
                query += ", follower_count"
            
            if 'following_count' in columns:
                query += ", following_count"
            
            query += " FROM register WHERE user_id = %s"
            print(f"执行SQL查询: {query}, user_id={user_id}")
            
            # 执行查询
            cursor.execute(query, (user_id,))
            user_data = cursor.fetchone()
            
            if not user_data:
                print(f"用户不存在: user_id={user_id}")
                return BaseResponse.error(404, "用户不存在")
            
            print(f"获取到用户数据: {user_data}")
            
            # 使用安全的方式构建用户对象
            user = {
                'user_id': user_data['user_id'],
                'user_name': user_data['user_name'],
                'user_create_time': user_data['user_create_time'],
                'like_count': user_data.get('like_count', 0),
                'follower_count': user_data.get('follower_count', 0),
                'following_count': user_data.get('following_count', 0)
            }
            
            return BaseResponse.success({"user": user})
        except Exception as e:
            print(f"获取用户信息失败: {str(e)}")
            return BaseResponse.error(500, f"服务器错误: {str(e)}")
        finally:
            cursor.close()
            db.close()
