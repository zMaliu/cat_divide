# -*- coding: utf-8 -*-
from app.database import get_db
from app.schemas.response import BaseResponse
from app.models.db_models import Post
import pymysql

class PostService:
    @staticmethod
    def create_post(title, content, user_id):
        db = get_db()
        cursor = db.cursor()
        try:
            default_img = "/default.jpg"
            cursor.execute("""
                INSERT INTO publish(title, content, img, publish_time, user_id)
                VALUES (%s, %s, %s, NOW(), %s)
            """, (title, content, default_img, user_id))
            db.commit()
            return BaseResponse.success(data={"success": True})
        except Exception as e:
            db.rollback()
            print(f"数据库错误: {str(e)}")
            return BaseResponse.error(500, "创建文章失败", data={"success": False})
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_posts(page=1, per_page=10, user_id=None):
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            offset = (page - 1) * per_page
            if user_id:
                cursor.execute("""
                SELECT 
                    p.article_id, 
                    p.user_id,
                    p.title, 
                    p.content, 
                    p.publish_time,
                    u.user_name,
                    COALESCE(ast.like_count, 0) as like_count,
                    (SELECT COUNT(*) FROM comments WHERE article_id = p.article_id) AS reply_count,
                    EXISTS(SELECT 1 FROM likes WHERE article_id = p.article_id AND user_id = %s) AS is_liked,
                    EXISTS(SELECT 1 FROM follows WHERE follower_id = %s AND followed_id = p.user_id) AS is_followed
                FROM publish p 
                JOIN register u ON p.user_id = u.user_id
                LEFT JOIN article_stats ast ON p.article_id = ast.article_id
                ORDER BY p.publish_time DESC
                LIMIT %s OFFSET %s
            """, (user_id, user_id, per_page, offset))
            else:
                cursor.execute("""
                SELECT 
                    p.article_id, 
                    p.user_id,
                    p.title, 
                    p.content, 
                    p.publish_time,
                    u.user_name,
                    COALESCE(ast.like_count, 0) as like_count,
                    (SELECT COUNT(*) FROM comments WHERE article_id = p.article_id) AS reply_count,
                    FALSE AS is_liked,
                    FALSE AS is_followed
                FROM publish p 
                JOIN register u ON p.user_id = u.user_id
                LEFT JOIN article_stats ast ON p.article_id = ast.article_id
                ORDER BY p.publish_time DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            posts = cursor.fetchall()
            return BaseResponse.success({"posts": posts})
        except Exception as e:
            return BaseResponse.error(500, f"获取文章列表失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_post_detail(article_id, user_id=None):
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            if user_id:
                cursor.execute("""
                SELECT 
                    p.*,
                    u.user_name,
                    COALESCE(ast.like_count, 0) as like_count,
                    EXISTS(SELECT 1 FROM likes WHERE article_id = p.article_id AND user_id = %s) AS is_liked,
                    EXISTS(SELECT 1 FROM follows WHERE follower_id = %s AND followed_id = p.user_id) AS is_followed
                FROM publish p
                JOIN register u ON p.user_id = u.user_id
                LEFT JOIN article_stats ast ON p.article_id = ast.article_id
                WHERE p.article_id = %s
            """, (user_id, user_id, article_id))
            else:
                cursor.execute("""
                SELECT 
                    p.*,
                    u.user_name,
                    COALESCE(ast.like_count, 0) as like_count,
                    FALSE AS is_liked,
                    FALSE AS is_followed
                FROM publish p
                JOIN register u ON p.user_id = u.user_id
                LEFT JOIN article_stats ast ON p.article_id = ast.article_id
                WHERE p.article_id = %s
            """, (article_id,))
            
            post = cursor.fetchone()
            if not post:
                return BaseResponse.error(404, "文章不存在")
            
            return BaseResponse.success({"post": post})
        except Exception as e:
            return BaseResponse.error(500, f"获取文章详情失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def update_post(article_id, title, content, user_id):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("SELECT user_id FROM publish WHERE article_id = %s", (article_id,))
            post = cursor.fetchone()
            
            if not post:
                return BaseResponse.error(404, "文章不存在")
            
            if post[0] != user_id:
                return BaseResponse.error(403, "无权修改此文章")
            
            cursor.execute("""
                UPDATE publish 
                SET title = %s, content = %s
                WHERE article_id = %s
            """, (title, content, article_id))
            db.commit()
            return BaseResponse.success()
        except Exception as e:
            db.rollback()
            return BaseResponse.error(500, f"更新文章失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def delete_post(article_id, user_id):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("SELECT user_id FROM publish WHERE article_id = %s", (article_id,))
            post = cursor.fetchone()
            
            if not post:
                return BaseResponse.error(404, "文章不存在")
            
            if post[0] != user_id:
                return BaseResponse.error(403, "无权删除此文章")
            
            cursor.execute("DELETE FROM publish WHERE article_id = %s", (article_id,))
            db.commit()
            return BaseResponse.success()
        except Exception as e:
            db.rollback()
            return BaseResponse.error(500, f"删除文章失败: {str(e)}")
        finally:
            cursor.close()
            db.close()
