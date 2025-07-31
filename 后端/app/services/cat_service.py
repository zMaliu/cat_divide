from app.database import get_db
from app.schemas.response import BaseResponse
import pymysql

class CatService:
    @staticmethod
    def create_cat(name, breed, age, gender, description, owner_id, image_url=None):
        db = get_db()
        cursor = db.cursor()
        try:
            # 如果提供了image_url，则使用它，否则使用默认图片
            if image_url:
                cursor.execute("""
                    INSERT INTO cats (name, breed, age, gender, description, image_url, owner_id, create_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """, (name, breed, age, gender, description, image_url, owner_id))
            else:
                cursor.execute("""
                    INSERT INTO cats (name, breed, age, gender, description, owner_id, create_time)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (name, breed, age, gender, description, owner_id))
            db.commit()
            return BaseResponse.success({"cat_id": cursor.lastrowid})
        except Exception as e:
            db.rollback()
            return BaseResponse.error(500, f"创建猫咪信息失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_cats(page=1, per_page=10):
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            offset = (page - 1) * per_page
            cursor.execute("""
                SELECT c.*, u.user_name as owner_name
                FROM cats c
                JOIN register u ON c.owner_id = u.user_id
                ORDER BY c.create_time DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            cats = cursor.fetchall()
            return BaseResponse.success({"cats": cats})
        except Exception as e:
            return BaseResponse.error(500, f"查询猫咪列表失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_cat_detail(cat_id):
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute("""
                SELECT c.*, u.user_name as owner_name
                FROM cats c
                JOIN register u ON c.owner_id = u.user_id
                WHERE c.cat_id = %s
            """, (cat_id,))
            cat = cursor.fetchone()
            if not cat:
                return BaseResponse.error(404, "猫咪信息不存在")
            return BaseResponse.success({"cat": cat})
        except Exception as e:
            return BaseResponse.error(500, f"查询猫咪详情失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def update_cat(cat_id, name=None, breed=None, age=None, gender=None, description=None, image_url=None, owner_id=None):
        db = get_db()
        cursor = db.cursor()
        try:
            # 验证猫咪是否存在且属于当前用户
            cursor.execute("SELECT owner_id FROM cats WHERE cat_id = %s", (cat_id,))
            cat = cursor.fetchone()
            if not cat:
                return BaseResponse.error(404, "猫咪信息不存在")

            cat_owner_id = cat[0] if isinstance(cat, tuple) else cat['owner_id']
            if cat_owner_id != owner_id:
                return BaseResponse.error(403, "无权限修改此猫咪信息")

            # 构建更新语句
            update_fields = []
            params = []

            if name is not None:
                update_fields.append("name = %s")
                params.append(name)
            if breed is not None:
                update_fields.append("breed = %s")
                params.append(breed)
            if age is not None:
                update_fields.append("age = %s")
                params.append(age)
            if gender is not None:
                update_fields.append("gender = %s")
                params.append(gender)
            if description is not None:
                update_fields.append("description = %s")
                params.append(description)
            if image_url is not None:  # 添加对image_url的处理
                update_fields.append("image_url = %s")
                params.append(image_url)

            if not update_fields:
                return BaseResponse.success({"message": "无更新内容"})

            params.append(cat_id)
            update_sql = f"UPDATE cats SET {', '.join(update_fields)}, update_time = NOW() WHERE cat_id = %s"

            cursor.execute(update_sql, params)
            db.commit()

            if cursor.rowcount == 0:
                return BaseResponse.error(404, "更新失败")

            return BaseResponse.success()
        except Exception as e:
            db.rollback()
            return BaseResponse.error(500, f"更新猫咪信息失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def delete_cat(cat_id, owner_id):
        db = get_db()
        cursor = db.cursor()
        try:
            # 验证猫咪是否存在且属于当前用户
            cursor.execute("SELECT owner_id FROM cats WHERE cat_id = %s", (cat_id,))
            cat = cursor.fetchone()
            if not cat:
                return BaseResponse.error(404, "猫咪信息不存在")

            cat_owner_id = cat[0] if isinstance(cat, tuple) else cat['owner_id']
            if cat_owner_id != owner_id:
                return BaseResponse.error(403, "无权限删除此猫咪信息")

            cursor.execute("DELETE FROM cats WHERE cat_id = %s", (cat_id,))
            db.commit()

            if cursor.rowcount == 0:
                return BaseResponse.error(404, "删除失败")

            return BaseResponse.success()
        except Exception as e:
            db.rollback()
            return BaseResponse.error(500, f"删除猫咪信息失败: {str(e)}")
        finally:
            cursor.close()
            db.close()