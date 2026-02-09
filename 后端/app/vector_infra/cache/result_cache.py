import logging
import time
import json
from redis import Redis
from config.vector_config import VectorConfig
from app.utils.security import get_redis_client

logger = logging.getLogger(__name__)

"结果缓存"
class ResultCache:
    def __init__(self):
        self.config = VectorConfig()
        self.redis = get_redis_client()
        self.cache_ttl = self.config.CACHE_TTL
    
    "获取缓存结果"
    def get(self, key: str):
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    "设置缓存结果"
    def set(self, key: str, value: dict, ttl: int = None):
        try:
            ttl = ttl or self.cache_ttl
            self.redis.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    "删除缓存结果"
    def delete(self, key: str):
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    "生成缓存键"
    def get_cache_key(self, vector: list, top_k: int = 5):
        vector_hash = hash(tuple(vector[:10]))  
        return f"vector_search:{vector_hash}:{top_k}"