import logging
import socket
import time
from pymilvus import connections
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
        
    "检查Milvus服务是否可访问"
    def check_service_availability(self, timeout=5):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((self.config.MILVUS_HOST, int(self.config.MILVUS_PORT)))
            sock.close()
            logger.info(f"Milvus service available at {self.config.MILVUS_HOST}:{self.config.MILVUS_PORT}")
            return True
        except socket.timeout:
            logger.error(f"Milvus service timeout at {self.config.MILVUS_HOST}:{self.config.MILVUS_PORT}")
            return False
        except socket.error as e:
            logger.error(f"Milvus service unavailable: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error checking Milvus service availability: {str(e)}")
            return False

    "检查连接是否有效"
    def is_connected(self):
        try:
            if connections.has_connection("default"):
                # 尝试执行一个简单的操作来验证连接是否有效
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking Milvus connection status: {str(e)}")
            return False

    "建立Milvus连接"
    def connect(self, timeout=10, retries=3):
        try:
            if self.is_connected():
                logger.info("Milvus connection already exists and is valid")
                return 
            
            logger.info(f"Attempting to connect to Milvus at {self.config.MILVUS_HOST}:{self.config.MILVUS_PORT}")
            
            for i in range(retries):
                # 先检查服务是否可访问
                if self.check_service_availability(timeout=3):
                    try:
                        connections.connect(
                            alias="default",
                            host=self.config.MILVUS_HOST,
                            port=self.config.MILVUS_PORT,
                            user=self.config.MILVUS_USER,
                            password=self.config.MILVUS_PASSWORD,
                            secure=self.config.MILVUS_SECURE
                        )
                        logger.info(f"Successfully connected to Milvus at {self.config.MILVUS_HOST}:{self.config.MILVUS_PORT} (attempt {i+1}/{retries})")
                        return
                    except Exception as e:
                        logger.error(f"Milvus connection error (attempt {i+1}/{retries}): {str(e)}")
                        if i == retries - 1:
                            raise
                        logger.info(f"Retrying Milvus connection in 2 seconds...")
                        time.sleep(2)
                else:
                    logger.warning(f"Milvus service not available at {self.config.MILVUS_HOST}:{self.config.MILVUS_PORT} (attempt {i+1}/{retries})")
                    if i == retries - 1:
                        raise Exception("Milvus service not available")
                    logger.info(f"Retrying Milvus service check in 2 seconds...")
                    time.sleep(2)
            
        except Exception as e:
            logger.error(f"Milvus connection error: {str(e)}")
            raise

    "断开Milvus连接"
    def disconnect(self):
        try:
            if connections.has_connection("default"):
                connections.disconnect("default")
                logger.info("Disconnected from Milvus")
            else:
                logger.info("No Milvus connection to disconnect")
        except Exception as e:
            logger.error(f"Error disconnecting from Milvus: {str(e)}")

    "获取单例实例"
    @classmethod
    def get_instance(cls):
        return cls()