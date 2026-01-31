# -*- coding: utf-8 -*-
from app.database import get_db
from app.schemas.response import BaseResponse
import pymysql

class FavoriteService:
    @staticmethod
    def favorite_article(article_id, user_id):
        """收藏帖子"""
        db = get_db()
        cursor = db.cursor()
        try:
            # 先检查帖子是否存在
            cursor.execute("SELECT 1 FROM publish WHERE article_id=%s", (article_id,))
            if not cursor.fetchone():
                return BaseResponse.error(404, "帖子不存在")
            
            # 检查是否已经收藏
            cursor.execute("SELECT 1 FROM favorites WHERE article_id=%s AND user_id=%s",
                           (article_id, user_id))
            if cursor.fetchone():
                return BaseResponse.error(400, "已经收藏过了")

            # 添加收藏记录
            cursor.execute("""
                INSERT INTO favorites (article_id, user_id)
                VALUES (%s, %s)
            """, (article_id, user_id))

            db.commit()
            return BaseResponse.success()
        except Exception as e:
            db.rollback()
            print(f"收藏失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return BaseResponse.error(500, f"收藏失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def unfavorite_article(article_id, user_id):
        """取消收藏"""
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("SELECT 1 FROM favorites WHERE article_id=%s AND user_id=%s",
                           (article_id, user_id))
            if not cursor.fetchone():
                return BaseResponse.error(400, "还没有收藏")

            cursor.execute("""
                DELETE FROM favorites WHERE article_id=%s AND user_id=%s
            """, (article_id, user_id))

            db.commit()
            return BaseResponse.success()

        except Exception as e:
            db.rollback()
            print(f"取消收藏失败: {str(e)}")
            return BaseResponse.error(500, f"取消收藏失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_user_favorite_posts(user_id, page=1, per_page=20):
        """获取用户收藏的所有帖子"""
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            offset = (page - 1) * per_page
            
            # 查询用户收藏的所有帖子，包含帖子详细信息
            cursor.execute("""
                SELECT 
                    p.article_id, 
                    p.user_id,
                    p.title, 
                    p.content, 
                    p.img,
                    p.publish_time,
                    u.user_name,
                    COALESCE(ast.like_count, 0) as like_count,
                    (SELECT COUNT(*) FROM comments WHERE article_id = p.article_id) AS reply_count,
                    TRUE AS is_liked,
                    EXISTS(SELECT 1 FROM likes WHERE article_id = p.article_id AND user_id = %s) AS is_liked_by_user,
                    EXISTS(SELECT 1 FROM follows WHERE follower_id = %s AND followed_id = p.user_id) AS is_followed,
                    TRUE AS is_favorited,
                    f.favorite_time as favorited_time
                FROM favorites f
                JOIN publish p ON f.article_id = p.article_id
                JOIN register u ON p.user_id = u.user_id
                LEFT JOIN article_stats ast ON p.article_id = ast.article_id
                WHERE f.user_id = %s
                ORDER BY f.favorite_time DESC
                LIMIT %s OFFSET %s
            """, (user_id, user_id, user_id, per_page, offset))
            
            posts = cursor.fetchall()
            
            # 获取总数
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM favorites
                WHERE user_id = %s
            """, (user_id,))
            total_result = cursor.fetchone()
            total = total_result['total'] if total_result else 0
            
            # 格式化返回数据
            posts_list = []
            for post in posts:
                posts_list.append({
                    "article_id": post["article_id"],
                    "user_id": post["user_id"],
                    "title": post["title"],
                    "content": post["content"],
                    "img": post["img"],
                    "publish_time": post["publish_time"].strftime("%Y-%m-%d %H:%M:%S") if post["publish_time"] else None,
                    "user_name": post["user_name"],
                    "like_count": post["like_count"],
                    "reply_count": post["reply_count"],
                    "is_liked": bool(post["is_liked_by_user"]),
                    "is_followed": bool(post["is_followed"]),
                    "is_favorited": bool(post["is_favorited"]),
                    "favorited_time": post["favorited_time"].strftime("%Y-%m-%d %H:%M:%S") if post["favorited_time"] else None
                })
            
            return BaseResponse.success(data={
                "posts": posts_list,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0
            })
        except Exception as e:
            print(f"获取收藏帖子失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return BaseResponse.error(500, f"获取收藏帖子失败: {str(e)}")
        finally:
            cursor.close()
            db.close()
