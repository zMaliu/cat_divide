import logging
import numpy as np
from pymilvus import Collection,utility,FieldSchema,CollectionSchema,DataType
from config.vector_config import VectorConfig
from .collection_manager import MilvusCollectionManager

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
        # self.connection_manager = MilvusConnectionManager.get_instance()
        self.connection_manager.connect()
        self.collection=self._get_or_create_collection()

    def _get_or_create_collection(self):
        if utility.has_collection(self.config.VECTOR_COLLECTION_NAME):
            return Collection(self.config.VECTOR_COLLECTION_NAME)
        
        "定义集合模式"
        fields=[
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
            FieldSchema(name="cat_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.config.VECTOR_DIMENSION),
            FieldSchema(name="image_path", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="created_at", dtype=DataType.INT64)
        ]

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
        
        return collection
    
    "插入向量与元数据"
    def insert(self,vectors:list,metadatas:list):
        try:
            data = [
                [m["id"] for m in metadatas],
                [m["cat_id"] for m in metadatas],
                [m["user_id"] for m in metadatas],
                vectors,
                [m["image_path"] for m in metadatas],
                [m["created_at"] for m in metadatas]
            ]
            
            self.collection.insert(data)
            self.collection.flush()
            return True
         
        except Exception as e:
            logger.error(f"Vector insertion error: {str(e)}")
            return False

    "搜索向量"
    def search(self, vector: list, top_k: int):
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