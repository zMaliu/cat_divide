from app.database import get_db
from app.schemas.response import BaseResponse
import pymysql

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

    @staticmethod
    def unfollow_user(follower_id, followed_id):
        if follower_id == followed_id:
            return BaseResponse.error(400, "不能关注自己")

        db = get_db()
        cursor = db.cursor()
        try:
            # 检查是否已关注
            cursor.execute("SELECT 1 FROM follows WHERE follower_id=%s AND followed_id=%s",
                           (follower_id, followed_id))
            if not cursor.fetchone():
                return BaseResponse.error(400, "尚未关注该用户")

            # 删除关注关系
            cursor.execute("""
                DELETE FROM follows WHERE follower_id=%s AND followed_id=%s
            """, (follower_id, followed_id))

            # 更新用户统计
            cursor.execute("""
                UPDATE register 
                SET follower_count = follower_count - 1 
                WHERE user_id = %s AND follower_count > 0
            """, (followed_id,))

            cursor.execute("""
                UPDATE register 
                SET following_count = following_count - 1 
                WHERE user_id = %s AND following_count > 0
            """, (follower_id,))

            db.commit()
            return BaseResponse.success()
        except Exception as e:
            db.rollback()
            return BaseResponse.error(500, f"取消关注失败: {str(e)}")
        finally:
            cursor.close()
            db.close()
            
    @staticmethod
    def get_followers(user_id, page=1, per_page=10):
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            offset = (page - 1) * per_page
            cursor.execute("""
                SELECT r.user_id, r.user_name, r.user_create_time
                FROM follows f
                JOIN register r ON f.follower_id = r.user_id
                WHERE f.followed_id = %s
                ORDER BY f.follow_time DESC
                LIMIT %s OFFSET %s
            """, (user_id, per_page, offset))
            followers = cursor.fetchall()
            return BaseResponse.success({"followers": followers})
        except Exception as e:
            return BaseResponse.error(500, f"获取粉丝列表失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_followings(user_id, page=1, per_page=10):
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            offset = (page - 1) * per_page
            cursor.execute("""
                SELECT r.user_id, r.user_name, r.user_create_time
                FROM follows f
                JOIN register r ON f.followed_id = r.user_id
                WHERE f.follower_id = %s
                ORDER BY f.follow_time DESC
                LIMIT %s OFFSET %s
            """, (user_id, per_page, offset))
            followings = cursor.fetchall()
            return BaseResponse.success({"followings": followings})
        except Exception as e:
            return BaseResponse.error(500, f"获取关注列表失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def check_follow_status(follower_id, followed_id):
        if follower_id == followed_id:
            return BaseResponse.success({"is_following": False})

        db = get_db()
        cursor = db.cursor()
        try:
            # 检查是否已关注
            cursor.execute("SELECT 1 FROM follows WHERE follower_id=%s AND followed_id=%s",
                           (follower_id, followed_id))
            is_following = cursor.fetchone() is not None
            
            return BaseResponse.success({"is_following": is_following})
        except Exception as e:
            return BaseResponse.error(500, f"检查关注状态失败: {str(e)}")
        finally:
            cursor.close()
            db.close()