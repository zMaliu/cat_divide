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
            # 简化查询，修复语法错误
            cursor.execute("""
            SELECT 
                p.article_id, 
                p.title, 
                p.content,
                p.img,
                p.publish_time,
                p.user_id,
                u.user_name as post_user_name,
                0 AS like_count,
                0 AS comment_count
            FROM publish p 
            JOIN register u ON p.user_id = u.user_id
            ORDER BY p.publish_time DESC
            LIMIT %s OFFSET %s
            """, (per_page, offset))
            posts=cursor.fetchall()
            
            # 检查表是否存在并获取点赞和评论数量
            try:
                # 先检查likes表是否存在
                cursor.execute("SHOW TABLES LIKE 'likes'")
                likes_exists = cursor.fetchone() is not None
                print(f"likes表是否存在: {likes_exists}")
                
                # 先检查comments表是否存在
                cursor.execute("SHOW TABLES LIKE 'comments'")
                comments_exists = cursor.fetchone() is not None
                print(f"comments表是否存在: {comments_exists}")
                
                for post in posts:
                    # 获取点赞数
                    if likes_exists:
                        try:
                            like_cursor = db.cursor()
                            like_cursor.execute("SELECT COUNT(*) AS count FROM likes WHERE article_id = %s", (post['article_id'],))
                            result = like_cursor.fetchone()
                            post['like_count'] = result['count'] if isinstance(result, dict) else result[0]
                            like_cursor.close()
                        except Exception as e:
                            print(f"获取点赞数失败: {str(e)}")
                            post['like_count'] = 0
                    else:
                        post['like_count'] = 0
                    
                    # 获取评论数
                    if comments_exists:
                        try:
                            comment_cursor = db.cursor()
                            comment_cursor.execute("SELECT COUNT(*) AS count FROM comments WHERE article_id = %s", (post['article_id'],))
                            result = comment_cursor.fetchone()
                            post['comment_count'] = result['count'] if isinstance(result, dict) else result[0]
                            comment_cursor.close()
                        except Exception as e:
                            print(f"获取评论数失败: {str(e)}")
                            post['comment_count'] = 0
                    else:
                        post['comment_count'] = 0
            except Exception as e:
                print(f"检查表结构失败: {str(e)}")
                # 如果出错，只使用默认值
                
            return BaseResponse.success({"posts": posts})
        except Exception as e:
            print(f"查询失败: {str(e)}")
            return BaseResponse.error(500, f"查询失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_post_detail(article_id):
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            # 简化查询，避免子查询
            cursor.execute("""
                SELECT 
                    p.*, 
                    u.user_name
                FROM publish p
                JOIN register u ON p.user_id = u.user_id
                WHERE p.article_id = %s
            """, (article_id,))
            post = cursor.fetchone()
            if not post:
                return BaseResponse.error(404, "文章不存在")
                
            # 检查likes表是否存在并获取点赞数
            try:
                cursor.execute("SHOW TABLES LIKE 'likes'")
                likes_exists = cursor.fetchone() is not None
                
                if likes_exists:
                    # 单独查询点赞数
                    like_cursor = db.cursor()
                    like_cursor.execute("SELECT COUNT(*) AS count FROM likes WHERE article_id = %s", (article_id,))
                    result = like_cursor.fetchone()
                    post['like_count'] = result['count'] if isinstance(result, dict) else result[0]
                    like_cursor.close()
                else:
                    post['like_count'] = 0
            except Exception as e:
                print(f"获取点赞数失败: {str(e)}")
                post['like_count'] = 0
            
            return BaseResponse.success({"post": post})
        except Exception as e:
            print(f"查询失败: {str(e)}")
            return BaseResponse.error(500, f"查询失败: {str(e)}")
        finally:
            cursor.close()
            db.close()
