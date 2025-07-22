from app.database import get_db
from app.schemas.response import BaseResponse
import pymysql

class CommentService:
    @staticmethod
    def create_comment(article_id, content, user_id):
        db = get_db()
        cursor = db.cursor()
        try:
            # 验证文章是否存在
            cursor.execute("SELECT 1 FROM publish WHERE article_id = %s", (article_id,))
            if not cursor.fetchone():
                return BaseResponse.error(404, "文章不存在")

            cursor.execute("""
                INSERT INTO comments (article_id, user_id, article_content, comment_time)
                VALUES (%s, %s, %s, NOW())
            """, (article_id, user_id, content))
            db.commit()
            return BaseResponse.success()
        except Exception as e:
            db.rollback()
            return BaseResponse.error(500, f"评论失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_comments(article_id, page=1, per_page=10):
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            offset = (page - 1) * per_page
            cursor.execute("""
                SELECT c.*, u.user_name 
                FROM comments c
                JOIN register u ON c.user_id = u.user_id
                WHERE c.article_id = %s
                ORDER BY comment_time DESC
                LIMIT %s OFFSET %s
            """, (article_id, per_page, offset))
            comments = cursor.fetchall()
            return BaseResponse.success({"comments": comments})
        except Exception as e:
            return BaseResponse.error(500, f"查询失败: {str(e)}")
        finally:
            cursor.close()
            db.close()
