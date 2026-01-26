import logging
import numpy as np
import time
from app.vector_infra.milvus.vector_respository import MilvusVectorRepository
from app.vector_infra.cache.result_cache import ResultCache
from app.services.yolo_service import YOLOService
from app.utils.vector_utils import normalize_vector

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
    
    "特征提取（未完善）"
    @staticmethod
    def extract_features(image_path: str) -> list:
        try:
            features = YOLOService.extract_features(image_path)
            return normalize_vector(features)
        except Exception as e:
            logger.error(f"Feature extraction error: {str(e)}")
            raise
    
    "为猫咪添加向量"
    @classmethod
    def add_cat_vector(cls, cat_id: str, user_id: str, image_path: str) -> bool:
        try:
            vector = cls.extract_features(image_path)
            metadata = {
                "id": f"vec_{cat_id}_{int(time.time())}",
                "cat_id": cat_id,
                "user_id": user_id,
                "image_path": image_path,
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
            # TODO: 开发获取相似猫咪的方法，获取相似猫列表返回
            results = repository.get_similar_cats(vector, threshold, top_k)
            cache.set(cache_key, results)
            
            return results
        except Exception as e:
            logger.error(f"Search similar cats error: {str(e)}")
            return []