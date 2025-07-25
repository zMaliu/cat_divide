from app.database import get_db
from app.schemas.response import BaseResponse
from app.models.db_models import Post
import pymysql

class PostService:
    @staticmethod
    def create_post(title,content,user_id):
        db=get_db()
        cursor=db.cursor()
        try:
            default_img="/default.jpg"
            cursor.execute("""
                INSERT INTO publish(title,content,img,publish_time,user_id)
                VALUES (%s,%s,%s,NOW(),%s)
            """,(title,content,default_img,user_id))
            db.commit()
            return BaseResponse.success(data={"success":True})
        except Exception as e:
            db.rollback()
            print(f"数据库错误：{str(e)}")
            return BaseResponse.error(500,f"创建失败：{str(e)}",data={"success":False})
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
            SELECT 
                p.article_id, 
                p.title, 
                p.content, 
                p.publish_time,
                u.user_name,
                p.like_count,
            FROM publish p 
            JOIN register u ON p.user_id = u.user_id
            ORDER BY p.publish_time DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))
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
                SELECT p.*, u.user_name,p.like_count ,
                    EXISTS(SELECT 1 FROM likes WHERE article_id = p.article_id AND user_id = %s) AS is_liked
                FROM publish p
                JOIN register u ON p.user_id = u.user_id
                WHERE p.article_id = %s
            """, (article_id,article_id))
            post = cursor.fetchone()
            if not post:
                return BaseResponse.error(404, "文章不存在")
            return BaseResponse.success({"post": post})
        except Exception as e:
            return BaseResponse.error(500, f"查询失败: {str(e)}")
        finally:
            cursor.close()
            db.close()
