import logging
import numpy as np
import time

from app.schemas.response import BaseResponse
from app.services import cat_service
from app.vector_infra.milvus.vector_respository import MilvusVectorRepository
from app.vector_infra.cache.result_cache import ResultCache
from app.services.feature_service import extract_features_from_path
from app.utils.vector_utils import normalize_vector
from app.services.cat_service import CatService

logger = logging.getLogger(__name__)

"向量服务"
class VectorService:
    _repository = None
    _cache = None
    
    @classmethod
    def get_repository(cls):
        if cls._repository is None:
            cls._repository = MilvusVectorRepository()
        return cls._repository
    
    @classmethod
    def get_cache(cls):
        if cls._cache is None:
            cls._cache = ResultCache()
        return cls._cache
    
    "特征提取：使用 CatReID 从图片路径提取 256 维向量并归一化"
    @staticmethod
    def extract_features(image_path: str) -> list:
        try:
            features = extract_features_from_path(image_path)
            return normalize_vector(features)
        except Exception as e:
            logger.error(f"Feature extraction error: {str(e)}")
            raise
    
    "为猫咪添加向量"
    @classmethod
    def add_cat_vector(cls, cat_id, user_id, image_path: str) -> bool:
        try:
            vector = cls.extract_features(image_path)
            # Milvus 中 cat_id / user_id 为 INT64，与 MySQL 一致
            metadata = {
                "id": f"vec_{str(cat_id)}_{str(int(time.time()))}",
                "cat_id": int(cat_id),
                "user_id": int(user_id),
                "image_path": str(image_path),
                "created_at": int(time.time())
            }
            
            repository = cls.get_repository()
            return repository.insert([vector], [metadata])
        except Exception as e:
            logger.error(f"Add cat vector error: {str(e)}")
            return False
    
    "搜索相似猫咪"
    @classmethod
    def search_similar_cats(cls, vector: list, threshold: float = 0.7, top_k: int = 5) -> list:
        try:
            cache = cls.get_cache()
            cache_key = cache.get_cache_key(vector, top_k)
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            repository = cls.get_repository()

            # 获取相似猫咪的id,图片路径和相似度
            milvus_results = repository.get_similar_cat(vector, threshold, top_k)
            if not milvus_results:
                return []


            # 根据相似猫咪的id查询猫咪完整信息（Milvus 返回 int，batch_get 键为 str）
            cat_ids = list(set([int(r["cat_id"]) for r in milvus_results]))
            cats_info = CatService.batch_get_cats_by_ids(cat_ids)

            # 封装完整的相似猫咪信息返回
            final_response = []
            for result in milvus_results:
                db_info = cats_info.get(str(result["cat_id"]))
                if not db_info:
                    logger.warning("%s exists in Milvus but not in MySQL", result["cat_id"])
                    continue

                final_response.append({
                    "milvus_id": result.get("id"),
                    "cat_id": db_info.get("cat_id"),
                    "cat_name": db_info.get("name"),
                    "breed": db_info.get("breed"),
                    "age": db_info.get("age"),
                    "gender": db_info.get("gender"),
                    "description": db_info.get("description"),
                    "image_url": db_info.get("image_url"),
                    "similarity": result["similarity"],  # 0-1范围，建议前端显示为百分比
                    "similarity_percent": round(result["similarity"] * 100, 2),  # 88.5%
                })

            # 按相似度降序排列（越高越相似）
            final_response.sort(key=lambda x: x["similarity"], reverse=True)

            # 缓存结果
            cache.set(cache_key, final_response, ttl=300)  # 5分钟过期

            return final_response

        except Exception as e:
            logger.error(f"Search similar cats error: {str(e)}")
            return []