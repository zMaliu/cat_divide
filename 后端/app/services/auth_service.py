import hashlib
import uuid
from app.database import get_db
from app.schemas.response import BaseResponse

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

            user_id, db_password = user
            hashed_pwd = hashlib.md5(password.encode()).hexdigest()

            if hashed_pwd != db_password:
                return BaseResponse.error(401, "密码错误")

            token = str(uuid.uuid4())
            token_map[token] = user_id
            return BaseResponse.success({"user_id": user_id, "token": token})
        except Exception as e:
            return BaseResponse.error(500, f"服务器错误: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def verify_token(token):
        if token.startswith("Bearer "):
            token=token[7:]
        return token_map.get(token)
