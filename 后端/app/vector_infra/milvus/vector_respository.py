import logging
import numpy as np
from pymilvus import Collection,utility,FieldSchema,CollectionSchema,DataType
from config.vector_config import VectorConfig
from .collection_manager import MilvusCollectionManager
from .connection_manager import MilvusConnectionManager

logger=logging.getLogger(__name__)

"向量存储库接口"
class VectorRepository:
    def insert(self,vector:list,metadata:list):
        raise NotImplementedError
    def search(self,vector:list,top_k:int):
        raise NotImplementedError
    def get_by_id(self,id:str):
        raise NotImplementedError
    def delete_by_id(self,id:str):
        raise NotImplementedError
    
"Milvus向量储存库"
class MilvusVectorRepository(VectorRepository):
    def __init__(self):
        self.config = VectorConfig()
        self.connection_manager = MilvusConnectionManager.get_instance()
        self.collection = None
        try:
            self.connection_manager.connect()
            self.collection = self._get_or_create_collection()
        except Exception as e:
            logger.error(f"Failed to initialize MilvusVectorRepository: {str(e)}")
            # 不抛出异常，允许应用在Milvus不可用时继续运行
            self.collection = None
    
    "检查存储库是否可用"
    def is_available(self):
        return self.collection is not None

    def _get_or_create_collection(self):
        # 强制删除旧集合，确保重新创建正确的schema
        if utility.has_collection(self.config.VECTOR_COLLECTION_NAME):
            logger.info(f"删除现有集合: {self.config.VECTOR_COLLECTION_NAME}")
            try:
                utility.drop_collection(self.config.VECTOR_COLLECTION_NAME)
                logger.info("集合删除成功")
            except Exception as e:
                logger.error(f"删除集合失败: {str(e)}")
        
        # 打印DataType枚举值，用于调试
        logger.info(f"DataType枚举值: INT64={DataType.INT64}, VARCHAR={DataType.VARCHAR}, FLOAT_VECTOR={DataType.FLOAT_VECTOR}")
        
        "定义集合模式（cat_id / user_id 与 MySQL 一致为 INT64）"
        fields=[
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
            FieldSchema(name="cat_id", dtype=DataType.INT64),
            FieldSchema(name="user_id", dtype=DataType.INT64),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.config.VECTOR_DIMENSION),
            FieldSchema(name="image_path", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="created_at", dtype=DataType.INT64)
        ]
        
        logger.info(f"创建新集合，字段定义: {[f'{f.name}:{f.dtype}' for f in fields]}")

        schema=CollectionSchema(
            fields=fields, 
            description="Vector collection"
            )
        
        collection=Collection(
            name=self.config.VECTOR_COLLECTION_NAME,
            schema=schema
            )
        
        "创建索引"
        index_params={
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
        collection.create_index(
            field_name="vector",
            index_params=index_params
            )
        
        logger.info(f"成功创建新集合: {self.config.VECTOR_COLLECTION_NAME}")
        return collection
    
    "插入向量与元数据"
    def insert(self,vectors:list,metadatas:list):
        if not self.is_available():
            logger.error("Milvus collection not available for insertion")
            return False
        
        try:
            # 检查输入数据
            logger.info(f"准备插入 {len(metadatas)} 条数据到Milvus")
            logger.info(f"第一条数据示例: {metadatas[0] if metadatas else '空'}")
            logger.info(f"向量维度: {len(vectors[0]) if vectors else 0}")
            
            # 使用正确的格式插入数据
            # Milvus 2.4.0 推荐使用字典列表形式
            insert_data = []
            for i, metadata in enumerate(metadatas):
                # 确保所有字段类型正确
                item = {
                    "id": str(metadata["id"]),  # VARCHAR 类型
                    "cat_id": int(metadata["cat_id"]),  # INT64 类型
                    "user_id": int(metadata["user_id"]),  # INT64 类型
                    "vector": vectors[i],  # FLOAT_VECTOR 类型
                    "image_path": str(metadata["image_path"]),  # VARCHAR 类型
                    "created_at": int(metadata["created_at"])  # INT64 类型
                }
                insert_data.append(item)
            
            logger.info(f"插入数据格式: {insert_data[0] if insert_data else '空'}")
            
            # 执行插入
            self.collection.insert(insert_data)
            self.collection.flush()
            logger.info("数据插入成功")
            return True
         
        except Exception as e:
            logger.error(f"Vector insertion error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    "搜索向量"
    def search(self, vector: list, top_k: int):
        if not self.is_available():
            logger.error("Milvus collection not available for search")
            return []
        
        try:
            self.collection.load()
            search_params = {
                "metric_type": "L2",
                "params": {"nprobe": 16}
            }
            
            results = self.collection.search(
                data=[vector],
                anns_field="vector",
                param=search_params,
                limit=top_k,
                output_fields=["id", "cat_id", "user_id", "image_path"]
            )
            
            hits = results[0]
            results_list = []
            for hit in hits:
                results_list.append({
                    "id": hit.entity.get("id"),
                    "cat_id": hit.entity.get("cat_id"),
                    "user_id": hit.entity.get("user_id"),
                    "image_path": hit.entity.get("image_path"),
                    "distance": hit.distance
                })
            
            return results_list
        except Exception as e:
            logger.error(f"Vector search error: {str(e)}")
            return []
        
    "根据ID获取向量"
    def get_by_id(self,id:str):
        if not self.is_available():
            logger.error("Milvus collection not available for get_by_id")
            return None
        
        try:
            self.collection.load()
            expr = f'id == "{id}"'
            results = self.collection.query(expr, output_fields=["*"])
            
            if results:
                return {
                    "id": results[0]["id"],
                    "cat_id": results[0]["cat_id"],
                    "user_id": results[0]["user_id"],
                    "vector": results[0]["vector"],
                    "image_path": results[0]["image_path"],
                    "created_at": results[0]["created_at"]
                }
            return None
        except Exception as e:
            logger.error(f"Get vector by ID error: {str(e)}")
            return None
    
    "通过ID删除向量"
    def delete_by_id(self, id:str):
        if not self.is_available():
            logger.error("Milvus collection not available for delete_by_id")
            return False
        
        try:
            expr = f'id == "{id}"'
            result = self.collection.delete(expr)
            self.collection.flush()
            return result.delete_count > 0
        except Exception as e:
            logger.error(f"Delete vector by ID error: {str(e)}")
            return False
    
    "获取相似猫咪个体"
    def get_similar_cat(self,vector:list,threshold:float,top_k:int):
        if not self.is_available():
            logger.error("Milvus collection not available for get_similar_cat")
            return []
        
        results = self.search(vector, top_k)
        similar_cats = []
        for result in results:
            # 距离转换为相似度 
            similarity = 1 / (1 + result["distance"])
            if similarity >= threshold:
                similar_cats.append({
                    "id": result["id"],
                    "cat_id": result["cat_id"],
                    "similarity": similarity,
                    "image_path": result["image_path"]
                })
        
        return similar_cats