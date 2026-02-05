# -*- coding: utf-8 -*-
from app.database import get_db
from app.schemas.response import BaseResponse
import pymysql

class CatService:
    @staticmethod
    def create_cat(name, breed, age, gender, description, owner_id, image_url=None):
        db = get_db()
        cursor = db.cursor()
        try:
            # 根据是否有image_url决定插入语句
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
            cat_id = cursor.lastrowid
            
            if not cat_id:
                raise Exception("无法获取创建的猫咪ID")
            return BaseResponse.success({"cat_id": cat_id})
        except Exception as e:
            db.rollback()
            import traceback
            error_msg = str(e)
            return BaseResponse.error(500, f"创建猫咪信息失败: {error_msg}")
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
            return BaseResponse.error(500, f"获取猫咪列表失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_cat_by_id(cat_id):
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
                return BaseResponse.error(404, "猫咪不存在")
            return BaseResponse.success({"cat": cat})
        except Exception as e:
            return BaseResponse.error(500, f"获取猫咪详情失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def batch_get_cats_by_ids(cat_ids):
        """根据 cat_id 列表批量查询猫咪信息，返回 dict：cat_id -> 猫咪信息（含 name, breed, age, gender, description, image_url 等）。"""
        if not cat_ids:
            return {}
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            placeholders = ",".join(["%s"] * len(cat_ids))
            cursor.execute(
                f"SELECT c.cat_id, c.name, c.breed, c.age, c.gender, c.description, c.image_url, c.owner_id "
                f"FROM cats c WHERE c.cat_id IN ({placeholders})",
                tuple(cat_ids),
            )
            rows = cursor.fetchall()
            return {str(row["cat_id"]): row for row in rows}
        except Exception as e:
            return {}
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def update_cat(cat_id, name=None, breed=None, age=None, gender=None, description=None, image_url=None, owner_id=None):
        db = get_db()
        cursor = db.cursor()
        try:
            # 检查猫咪是否存在且属于当前用户
            cursor.execute("SELECT owner_id FROM cats WHERE cat_id = %s", (cat_id,))
            cat = cursor.fetchone()
            if not cat:
                return BaseResponse.error(404, "猫咪不存在")

            cat_owner_id = cat[0] if isinstance(cat, tuple) else cat['owner_id']
            if cat_owner_id != owner_id:
                return BaseResponse.error(403, "无权限修改此猫咪信息")

            # 构建更新字段
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
            if image_url is not None:  # 允许image_url为空字符串
                update_fields.append("image_url = %s")
                params.append(image_url)

            if not update_fields:
                return BaseResponse.success({"message": "没有需要更新的字段"})

            params.append(cat_id)
            update_sql = f"UPDATE cats SET {', '.join(update_fields)}, update_time = NOW() WHERE cat_id = %s"

            cursor.execute(update_sql, params)
            db.commit()

            if cursor.rowcount == 0:
                return BaseResponse.error(404, "更新失败，猫咪不存在")

            return BaseResponse.success({"message": "更新成功"})
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
            # 检查猫咪是否存在且属于当前用户
            cursor.execute("SELECT owner_id FROM cats WHERE cat_id = %s", (cat_id,))
            cat = cursor.fetchone()
            if not cat:
                return BaseResponse.error(404, "猫咪不存在")

            cat_owner_id = cat[0] if isinstance(cat, tuple) else cat['owner_id']
            if cat_owner_id != owner_id:
                return BaseResponse.error(403, "无权限删除此猫咪信息")

            cursor.execute("DELETE FROM cats WHERE cat_id = %s", (cat_id,))
            db.commit()

            if cursor.rowcount == 0:
                return BaseResponse.error(404, "删除失败，猫咪不存在")

            return BaseResponse.success({"message": "删除成功"})
        except Exception as e:
            db.rollback()
            return BaseResponse.error(500, f"删除猫咪信息失败: {str(e)}")
        finally:
            cursor.close()
            db.close()