import os
from typing import Dict,Any

"milvus config"
class  VectorConfig:
    def __init__(self):
        self._load_environment()
    
    def _load_environment(self):
        self.MILVUS_HOST = os.getenv('MILVUS_HOST', 'localhost')
        self.MILVUS_PORT = os.getenv('MILVUS_PORT', '19530')
        self.MILVUS_USER = os.getenv('MILVUS_USER', '')
        self.MILVUS_PASSWORD = os.getenv('MILVUS_PASSWORD', '')
        self.MILVUS_SECURE = os.getenv('MILVUS_SECURE', 'false').lower() == 'true'
        
        self.VECTOR_COLLECTION_NAME = os.getenv('VECTOR_COLLECTION_NAME', 'cat_vectors')
        self.VECTOR_DIMENSION = int(os.getenv('VECTOR_DIMENSION', '256'))
        
        self.CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))
        self.CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', '1000'))
        
        self.FEATURE_MODEL_PATH = os.getenv('FEATURE_MODEL_PATH', '')
        self.FEATURE_MODEL_TYPE = os.getenv('FEATURE_MODEL_TYPE', '')
    
    "转换为字典格式"
    def to_dict(self)->Dict[str,Any]:
        return {
            "milvus_host": self.MILVUS_HOST,
            "milvus_port": self.MILVUS_PORT,
            "milvus_user": self.MILVUS_USER,
            "milvus_password": self.MILVUS_PASSWORD,
            "milvus_secure": self.MILVUS_SECURE,
            "vector_collection_name": self.VECTOR_COLLECTION_NAME,
            "vector_dimension": self.VECTOR_DIMENSION,
            "cache_ttl": self.CACHE_TTL,
            "cache_max_size": self.CACHE_MAX_SIZE,
            "feature_model_path": self.FEATURE_MODEL_PATH,
            "feature_model_type": self.FEATURE_MODEL_TYPE
        }
