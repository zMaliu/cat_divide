import logging
import os
from app.services.vector_service import VectorService
from app.services.cat_service import CatService
from app.models.db_models import Cat

logger = logging.getLogger(__name__)

"个体识别服务"
class RecognitionService:
    @staticmethod
    def identify_cat(image_path: str, user_id: str = None, threshold: float = 0.7) -> dict:
        try:
            vector = VectorService.extract_features(image_path)
            results = VectorService.search_similar_cats(vector, threshold)
            
            if not results:
                return {
                    "identified": False,
                    "message": "未找到匹配的猫咪个体",
                    "candidates": []
                }
            
            # 获取完整的猫咪信息
            candidates = []
            for result in results:
                cat = CatService.get_cat_by_id(result["cat_id"])
                if cat:
                    candidates.append({
                        "cat": cat,
                        "similarity": result["similarity"],
                        "image_path": result["image_path"]
                    })
            
            # 如果提供了用户ID，优先返回该用户的猫
            if user_id:
                user_cats = [c for c in candidates if c["cat"].user_id == user_id]
                if user_cats:
                    return {
                        "identified": True,
                        "cat": user_cats[0]["cat"],
                        "similarity": user_cats[0]["similarity"],
                        "candidates": candidates
                    }
            
            # 返回最匹配的结果
            return {
                "identified": True,
                "cat": candidates[0]["cat"],
                "similarity": candidates[0]["similarity"],
                "candidates": candidates
            }
            
        except Exception as e:
            logger.error(f"Cat identification error: {str(e)}")
            return {
                "identified": False,
                "message": f"识别过程中出错: {str(e)}",
                "candidates": []
            }
    
    @staticmethod
    def register_new_cat(image_path: str, user_id: str, cat_data: dict) -> dict:
        try:
            cat = CatService.create_cat(user_id, cat_data)
            if not cat:
                return {"success": False, "message": "创建猫咪记录失败"}
            
            if not VectorService.add_cat_vector(cat.id, user_id, image_path):
                CatService.delete_cat(cat.id, user_id)
                return {"success": False, "message": "添加特征向量失败"}
            
            return {
                "success": True,
                "cat": cat,
                "message": "猫咪个体注册成功"
            }
            
        except Exception as e:
            logger.error(f"Register new cat error: {str(e)}")
            return {"success": False, "message": f"注册过程中出错: {str(e)}"}