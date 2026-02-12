import logging
from pymilvus import Collection, FieldSchema, CollectionSchema, DataType, utility
from config.vector_config import VectorConfig
from .connection_manager import MilvusConnectionManager

logger = logging.getLogger(__name__)


class MilvusCollectionManager:
    def __init__(self, config: VectorConfig | None = None):
        self.config = config or VectorConfig()
        self.connection_manager = MilvusConnectionManager.get_instance()

    def get_collection(self) -> Collection:
        self.connection_manager.connect()
        name = self.config.VECTOR_COLLECTION_NAME
        if not utility.has_collection(name):
            raise RuntimeError(f"Milvus collection not found: {name}")
        return Collection(name=name)

    def get_or_create_collection(self) -> Collection:
        self.connection_manager.connect()
        name = self.config.VECTOR_COLLECTION_NAME

        drop_on_start = getattr(self.config, "VECTOR_DROP_COLLECTION_ON_START", False)
        if utility.has_collection(name) and drop_on_start:
            try:
                utility.drop_collection(name)
            except Exception as e:
                logger.error("drop collection failed: %s", e)

        if utility.has_collection(name):
            collection = Collection(name=name)
            self.ensure_indexes(collection)
            return collection

        schema = CollectionSchema(fields=self._build_fields(), description="Vector collection")
        collection = Collection(name=name, schema=schema)
        self.ensure_indexes(collection)
        return collection

    def _build_fields(self) -> list[FieldSchema]:
        dim = int(getattr(self.config, "VECTOR_DIMENSION", 256))
        id_max_len = int(getattr(self.config, "VECTOR_ID_MAX_LENGTH", 100))
        image_path_max_len = int(getattr(self.config, "VECTOR_IMAGE_PATH_MAX_LENGTH", 255))

        return [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=id_max_len),
            FieldSchema(name="cat_id", dtype=DataType.INT64),
            FieldSchema(name="user_id", dtype=DataType.INT64),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="image_path", dtype=DataType.VARCHAR, max_length=image_path_max_len),
            FieldSchema(name="created_at", dtype=DataType.INT64),
        ]

    def ensure_indexes(self, collection: Collection) -> None:
        try:
            indexes = getattr(collection, "indexes", None) or []
            if any(getattr(idx, "field_name", None) == "vector" for idx in indexes):
                return

            index_type = getattr(self.config, "VECTOR_INDEX_TYPE", "IVF_FLAT")
            metric_type = getattr(self.config, "VECTOR_METRIC_TYPE", "L2")
            nlist = int(getattr(self.config, "VECTOR_NLIST", 128))

            collection.create_index(
                field_name="vector",
                index_params={
                    "index_type": index_type,
                    "metric_type": metric_type,
                    "params": {"nlist": nlist},
                },
            )
        except Exception as e:
            logger.error("ensure index failed: %s", e)