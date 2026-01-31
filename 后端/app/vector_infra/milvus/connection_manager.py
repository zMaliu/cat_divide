import logging
from pymilvus import connections,utility
from config.vector_config import VectorConfig

logger=logging.getLogger(__name__)

"Milvus连接管理"
class MilvusConnectionManager:
    _instance = None
    def  __new__(cls):
        if  cls._instance is None:
            cls._instance = super(MilvusConnectionManager, cls).__new__(cls)
            cls._instance._is_initialized = False
        return cls._instance
    def __init__(self):
        if not self._is_initialized:
            self.config = VectorConfig()
            self._is_initialized = True
        
    "建立Milvus连接"
    def connect(self):
        try:
            if connections.has_connection("default"):
                return 
            connections.connet(
                alias="default",
                host=self.config.MILVUS_HOST,
                port=self.config.MILVUS_PORT,
                user=self.config.MILVUS_USER,
                password=self.config.MILVUS_PASSWORD,
                secure=self.config.MILVUS_SECURE
            )

            if not utility.has_collection("default"):
                raise ConnectionError("Failed to establish Milvus connection")
            logger.info(f"Connected to Milvus at {self.config.MILVUS_HOST}:{self.config.MILVUS_PORT}")
            
        except Exception as e:
            logger.error(f"Milvus connection error: {str(e)}")
            raise

    "断开Milvus连接"
    def disconnect(self):
        try:
            connections.disconnect("default")
            logger.info("Disconnected from Milvus")
        except Exception as e:
            logger.error(f"Error disconnecting from Milvus: {str(e)}")

    "获取单例实例"
    @classmethod
    def get_instance(cls):
        return cls()