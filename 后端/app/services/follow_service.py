# -*- coding: utf-8 -*-
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
            # 检查是否已经关注
            cursor.execute("SELECT 1 FROM follows WHERE follower_id=%s AND followed_id=%s",
                           (follower_id, followed_id))
            if cursor.fetchone():
                return BaseResponse.error(400, "已经关注过了")

            # 添加关注关系
            cursor.execute("""
                INSERT INTO follows (follower_id, followed_id)
                VALUES (%s, %s)
            """, (follower_id, followed_id))

            # 不再直接更新用户关注数，而是通过视图获取实时数据

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
            return BaseResponse.error(400, "不能取消关注自己")

        db = get_db()
        cursor = db.cursor()
        try:
            # 检查是否已经关注
            cursor.execute("SELECT 1 FROM follows WHERE follower_id=%s AND followed_id=%s",
                           (follower_id, followed_id))
            if not cursor.fetchone():
                return BaseResponse.error(400, "还没有关注过")

            # 删除关注关系
            cursor.execute("""
                DELETE FROM follows WHERE follower_id=%s AND followed_id=%s
            """, (follower_id, followed_id))

            # 不再直接更新用户关注数，而是通过视图获取实时数据

            db.commit()
            return BaseResponse.success()
        except Exception as e:
            db.rollback()
            return BaseResponse.error(500, f"取消关注失败: {str(e)}")
        finally:
            cursor.close()
            db.close()
            
    @staticmethod
    def get_followers(user_id, page=1, per_page=20, current_user_id=None):
        """获取用户的粉丝列表"""
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            offset = (page - 1) * per_page
            
            # 查询粉丝列表，包含用户信息和是否互相关注
            if current_user_id:
                cursor.execute("""
                    SELECT 
                        r.user_id, 
                        r.user_name, 
                        r.user_avatar,
                        r.user_bio,
                        r.user_create_time,
                        f.follow_time,
                        EXISTS(SELECT 1 FROM follows WHERE follower_id = %s AND followed_id = r.user_id) AS is_following_back
                    FROM follows f
                    JOIN register r ON f.follower_id = r.user_id
                    WHERE f.followed_id = %s
                    ORDER BY f.follow_time DESC
                    LIMIT %s OFFSET %s
                """, (current_user_id, user_id, per_page, offset))
            else:
                cursor.execute("""
                    SELECT 
                        r.user_id, 
                        r.user_name, 
                        r.user_avatar,
                        r.user_bio,
                        r.user_create_time,
                        f.follow_time,
                        FALSE AS is_following_back
                    FROM follows f
                    JOIN register r ON f.follower_id = r.user_id
                    WHERE f.followed_id = %s
                    ORDER BY f.follow_time DESC
                    LIMIT %s OFFSET %s
                """, (user_id, per_page, offset))
            
            followers = cursor.fetchall()
            
            # 获取总数
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM follows
                WHERE followed_id = %s
            """, (user_id,))
            total_result = cursor.fetchone()
            total = total_result['total'] if total_result else 0
            
            # 格式化返回数据
            followers_list = []
            for follower in followers:
                followers_list.append({
                    "user_id": follower["user_id"],
                    "user_name": follower["user_name"],
                    "user_avatar": follower.get("user_avatar") or "/default.jpg",
                    "user_bio": follower.get("user_bio") or "",
                    "user_create_time": follower["user_create_time"].strftime("%Y-%m-%d %H:%M:%S") if follower["user_create_time"] else None,
                    "follow_time": follower["follow_time"].strftime("%Y-%m-%d %H:%M:%S") if follower["follow_time"] else None,
                    "is_following_back": bool(follower["is_following_back"])
                })
            
            return BaseResponse.success(data={
                "followers": followers_list,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0
            })
        except Exception as e:
            print(f"获取粉丝列表失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return BaseResponse.error(500, f"获取粉丝列表失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_followings(user_id, page=1, per_page=20, current_user_id=None):
        """获取用户的关注列表"""
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            offset = (page - 1) * per_page
            
            # 查询关注列表，包含用户信息
            cursor.execute("""
                SELECT 
                    r.user_id, 
                    r.user_name, 
                    r.user_avatar,
                    r.user_bio,
                    r.user_create_time,
                    f.follow_time
                FROM follows f
                JOIN register r ON f.followed_id = r.user_id
                WHERE f.follower_id = %s
                ORDER BY f.follow_time DESC
                LIMIT %s OFFSET %s
            """, (user_id, per_page, offset))
            
            followings = cursor.fetchall()
            
            # 获取总数
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM follows
                WHERE follower_id = %s
            """, (user_id,))
            total_result = cursor.fetchone()
            total = total_result['total'] if total_result else 0
            
            # 格式化返回数据
            followings_list = []
            for following in followings:
                followings_list.append({
                    "user_id": following["user_id"],
                    "user_name": following["user_name"],
                    "user_avatar": following.get("user_avatar") or "/default.jpg",
                    "user_bio": following.get("user_bio") or "",
                    "user_create_time": following["user_create_time"].strftime("%Y-%m-%d %H:%M:%S") if following["user_create_time"] else None,
                    "follow_time": following["follow_time"].strftime("%Y-%m-%d %H:%M:%S") if following["follow_time"] else None
                })
            
            return BaseResponse.success(data={
                "followings": followings_list,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0
            })
        except Exception as e:
            print(f"获取关注列表失败: {str(e)}")
            import traceback
            traceback.print_exc()
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
            # 检查是否已经关注
            cursor.execute("SELECT 1 FROM follows WHERE follower_id=%s AND followed_id=%s",
                           (follower_id, followed_id))
            is_following = cursor.fetchone() is not None
            
            return BaseResponse.success({"is_following": is_following})
        except Exception as e:
            return BaseResponse.error(500, f"检查关注状态失败: {str(e)}")
        finally:
            cursor.close()
            db.close()












