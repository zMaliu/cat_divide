from app.database import get_db
from app.schemas.response import BaseResponse
import pymysql

class LikeService:
    @staticmethod
    def like_article(article_id, user_id):
        db = get_db()
        cursor = db.cursor()
        try:
            # 检查是否已点赞
            cursor.execute("SELECT 1 FROM likes WHERE article_id=%s AND user_id=%s",
                           (article_id, user_id))
            if cursor.fetchone():
                return BaseResponse.error(400, "已点过赞")

            # 新增点赞
            cursor.execute("""
                INSERT INTO likes (article_id, user_id)
                VALUES (%s, %s)
            """, (article_id, user_id))

            # 更新文章点赞计数
            cursor.execute("""
                UPDATE publish SET like_count = like_count + 1 
                WHERE article_id = %s
            """, (article_id,))

            db.commit()
            return BaseResponse.success()
        except Exception as e:
            db.rollback()
            return BaseResponse.error(500, f"点赞失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def unlike_article(article_id,user_id):
        db=get_db()
        cursor=db.cursor()
        try:
            cursor.execute("SELECT 1 FROM likes WHERE article_id=%s AND user_id=%s",
                           (article_id,user_id))
            if not cursor.fetchone():
                return BaseResponse.error(400,"尚未点赞")

            cursor.execute("""
                DELETE FROM likes WHERE article_id=%s AND user_id=%s
            """, (article_id, user_id))

            cursor.execute("""
                UPDATE publish SET like_count = like_count - 1 
                WHERE article_id = %s
            """, (article_id,))

            db.commit()
            return BaseResponse.success()

        except Exception as e:
            db.rollback()
            return BaseResponse.error(500,f"取消点赞失败：{str(e)}")
        finally:
            cursor.close()
            db.close()
    @staticmethod
    def get_article_likes(article_id):
        # 获取文章点赞列表
        pass
