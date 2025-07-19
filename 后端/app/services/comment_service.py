from app.database import get_db
from app.schemas.response import BaseResponse
import pymysql
import traceback

class CommentService:
    @staticmethod
    def create_comment(article_id, content, user_id):
        print(f"创建评论: article_id={article_id}, content={content}, user_id={user_id}")
        db = get_db()
        cursor = db.cursor()
        try:
            # 验证文章是否存在
            cursor.execute("SELECT 1 FROM publish WHERE article_id = %s", (article_id,))
            if not cursor.fetchone():
                print("文章不存在")
                return BaseResponse.error(404, "文章不存在")

            cursor.execute("""
                INSERT INTO comments (article_id, user_id, article_content, comment_time)
                VALUES (%s, %s, %s, NOW())
            """, (article_id, user_id, content))
            db.commit()
            print("评论创建成功")
            return BaseResponse.success()
        except Exception as e:
            db.rollback()
            print(f"创建评论错误: {str(e)}")
            print(f"错误详情: {traceback.format_exc()}")
            return BaseResponse.error(500, f"评论失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_comments(article_id, page=1, per_page=10):
        print(f"获取评论: article_id={article_id}, page={page}, per_page={per_page}")
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            offset = (page - 1) * per_page
            print(f"查询评论: article_id={article_id}, page={page}, per_page={per_page}, offset={offset}")
            
            cursor.execute("""
                SELECT c.*, u.user_name 
                FROM comments c
                JOIN register u ON c.user_id = u.user_id
                WHERE c.article_id = %s
                ORDER BY comment_time DESC
                LIMIT %s OFFSET %s
            """, (article_id, per_page, offset))
            comments = cursor.fetchall()
            print(f"查询到 {len(comments)} 条评论")
            for comment in comments:
                print(f"评论: {comment}")
            result = BaseResponse.success({"comments": comments})
            print(f"返回结果: {result}")
            return result
        except Exception as e:
            print(f"查询评论错误: {str(e)}")
            print(f"错误详情: {traceback.format_exc()}")
            return BaseResponse.error(500, f"查询失败: {str(e)}")
        finally:
            cursor.close()
            db.close()
