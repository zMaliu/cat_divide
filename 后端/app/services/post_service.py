from app.database import get_db
from app.schemas.response import BaseResponse
from app.models.db_models import Post

class PostService:
    @staticmethod
    def create_post(title,content,user_id):
        db=get_db()
        cursor=db.cursor()
        try:
            cursor.execute("""
                INSERT INTO pulish(title,content,pulish_time,user_id)
                VALUES (%s,%s,NOW(),%s)
            """,(title,content,user_id))
            db.commit()
            return BaseResponse.success()
        except Exception as e:
            db.rollback()
            return BaseResponse.error(500,f"创建失败：{str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_posts(page=1,per_page=10):
        db=get_db()
        cursor=db.cursor(pymysql.cursors.DictCursor)
        try:
            offset=(page-1)*per_page
            cursor.execute("""
                SELECT p.*,user_name
                FROM publish p 
                JOIN register u ON p.user_id=u.user_id
                ORDER BY publish_time DESC
                LIMIT %s OFFSET %s
            """,(per_page,offset))
            posts=cursor.fetchall()
            return BaseResponse.success({"posts": posts})
        except Exception as e:
            return BaseResponse.error(500, f"查询失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_post_detail(article_id):
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute("""
                SELECT p.*, u.user_name 
                FROM publish p
                JOIN register u ON p.user_id = u.user_id
                WHERE p.article_id = %s
            """, (article_id,))
            post = cursor.fetchone()
            if not post:
                return BaseResponse.error(404, "文章不存在")
            return BaseResponse.success({"post": post})
        except Exception as e:
            return BaseResponse.error(500, f"查询失败: {str(e)}")
        finally:
            cursor.close()
            db.close()
