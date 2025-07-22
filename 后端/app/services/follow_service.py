from app.database import get_db
from app.schemas.response import BaseResponse

class FollowService:
    @staticmethod
    def follow_user(follower_id, followed_id):
        if follower_id == followed_id:
            return BaseResponse.error(400, "不能关注自己")

        db = get_db()
        cursor = db.cursor()
        try:
            # 检查是否已关注
            cursor.execute("SELECT 1 FROM follows WHERE follower_id=%s AND followed_id=%s",
                           (follower_id, followed_id))
            if cursor.fetchone():
                return BaseResponse.error(400, "已关注该用户")

            # 新增关注
            cursor.execute("""
                INSERT INTO follows (follower_id, followed_id)
                VALUES (%s, %s)
            """, (follower_id, followed_id))

            # 更新用户统计
            cursor.execute("""
                UPDATE register 
                SET follower_count = follower_count + 1 
                WHERE user_id = %s
            """, (followed_id,))

            cursor.execute("""
                UPDATE register 
                SET following_count = following_count + 1 
                WHERE user_id = %s
            """, (follower_id,))

            db.commit()
            return BaseResponse.success()
        except Exception as e:
            db.rollback()
            return BaseResponse.error(500, f"关注失败: {str(e)}")
        finally:
            cursor.close()
            db.close()
