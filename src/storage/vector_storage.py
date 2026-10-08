"""
向量存储模块
管理Milvus Lite向量索引
"""
from typing import Dict, List, Any
import numpy as np
import os
from config.milvus_config import MilvusConfig
from src.utils.logger import setup_logger

try:
    from pymilvus import MilvusClient, DataType
    MILVUS_LITE_AVAILABLE = True
except ImportError:
    MILVUS_LITE_AVAILABLE = False
    print("警告: pymilvus未安装，向量存储功能将不可用")

class VectorStorage:
    """向量存储系统（使用Milvus Lite）"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        # 从配置中读取设置
        milvus_config = MilvusConfig()
        conn_params = milvus_config.get_connection_params()
        
        self.collection_name = conn_params.get("collection_name", "rag_documents")
        self.dimension = 1024  # 默认嵌入维度
        self.uri = conn_params.get("uri", "sqlite:///data/milvus_lite.db")
        
        self._connect()
        self._init_collection()
    
    def _connect(self):
        """连接到Milvus Lite"""
        if not MILVUS_LITE_AVAILABLE:
            self.logger.warning("Milvus Lite不可用")
            return
        
        try:
            # 确保数据库目录存在
            if self.uri.startswith("sqlite:///"):
                db_path = self.uri.replace("sqlite:///", "")
                if not db_path.startswith(":memory:"):
                    # 使用绝对路径确保正确性
                    if not os.path.isabs(db_path):
                        db_path = os.path.join(os.getcwd(), db_path)
                    db_dir = os.path.dirname(db_path)
                    if db_dir and not os.path.exists(db_dir):
                        os.makedirs(db_dir, exist_ok=True)
                        self.logger.info(f"创建数据库目录: {db_dir}")
            
            # 使用Milvus Lite，数据存储在本地SQLite文件中
            self.client = MilvusClient(uri=self.uri)
            self.logger.info(f"成功连接到Milvus Lite，URI: {self.uri}")
            
        except Exception as e:
            self.logger.error(f"连接Milvus Lite失败: {e}")

    def _init_collection(self):
        """初始化集合"""
        if not MILVUS_LITE_AVAILABLE or not hasattr(self, 'client'):
            return
        
        try:
        # if True:
            # 检查集合是否存在
            collections = self.client.list_collections()
            if self.collection_name in collections:
                self.logger.info(f"集合 {self.collection_name} 已存在")
                return
            
            # 创建集合模式 - 使用正确的Schema对象
            from pymilvus import FieldSchema, CollectionSchema
            
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
                FieldSchema(name="summary", dtype=DataType.VARCHAR, max_length=1000),
                FieldSchema(name="content_link", dtype=DataType.VARCHAR, max_length=500),
                FieldSchema(name="content_type", dtype=DataType.VARCHAR, max_length=50),
                FieldSchema(name="source_book", dtype=DataType.VARCHAR, max_length=200),
                FieldSchema(name="source_page", dtype=DataType.INT64),
                FieldSchema(name="quality_score", dtype=DataType.FLOAT),
                FieldSchema(name="extraction_date", dtype=DataType.VARCHAR, max_length=50)
            ]
            
            schema = CollectionSchema(fields, "RAG文档向量索引")
            
            # 创建集合
            self.client.create_collection(
                collection_name=self.collection_name,
                schema=schema
            )
            
            # 创建索引
            index_params = {
                "index_type": "IVF_FLAT",
                "metric_type": "IP",
                "params": {"nlist": 128}
            }
            self.client.create_index(
                collection_name=self.collection_name,
                field_name="vector",
                index_params=index_params
            )
            
            self.logger.info(f"成功创建集合 {self.collection_name}")

        except Exception as e:
            self.logger.error(f"初始化集合失败: {e}")


    def store_vectors(self, vectors: List[List[float]], metadata: List[Dict]) -> None:
        """
        存储向量到Milvus Lite
        
        Args:
            vectors (List[List[float]]): 向量列表
            metadata (List[Dict]): 元数据列表
        """
        if not MILVUS_LITE_AVAILABLE or not hasattr(self, 'client'):
            self.logger.warning("向量存储不可用")
            return
        
        if not vectors or not metadata or len(vectors) != len(metadata):
            self.logger.warning("向量或元数据为空，或长度不匹配")
            return
        
        try:
            # 准备插入数据
            data = []
            for i in range(len(vectors)):
                data.append({
                    "vector": vectors[i],
                    "summary": metadata[i].get("summary", ""),
                    "content_link": metadata[i].get("content_link", ""),
                    "content_type": metadata[i].get("content_type", "text"),
                    "source_book": metadata[i].get("source_book", ""),
                    "source_page": metadata[i].get("source_page", 0),
                    "quality_score": metadata[i].get("quality_score", 1.0),
                    "extraction_date": metadata[i].get("extraction_date", "")
                })
            info = self.client.describe_collection(self.collection_name)
            print("collection_name",info)
            arr = np.array(vectors)
            print("Vectors shape:", arr.shape)
            
            # 插入数据
            self.client.insert(
                collection_name=self.collection_name,
                data=data
            )
            
            self.logger.info(f"成功存储 {len(vectors)} 个向量")
        except Exception as e:
            self.logger.error(f"存储向量失败: {e}")
    
    def search_vectors(self, query_vector: List[float], top_k: int = 5) -> List[Dict]:
        """
        搜索向量
        
        Args:
            query_vector (List[float]): 查询向量
            top_k (int): 返回结果数
        
        Returns:
            List[Dict]: 搜索结果
        """
        if not MILVUS_LITE_AVAILABLE or not hasattr(self, 'client'):
            self.logger.warning("向量存储不可用")
            return []
        
        try:
            # 搜索
            results = self.client.search(
                collection_name=self.collection_name,
                data=[query_vector],
                limit=top_k,
                output_fields=["summary", "content_link", "content_type", "source_book", "source_page", "quality_score"]
            )
            
            # 处理结果
            search_results = []
            if results:
                for hit in results[0]:  # 第一个查询的结果
                    search_results.append({
                        "id": hit.get("id", 0),
                        "distance": hit.get("distance", 0.0),
                        "metadata": {
                            "summary": hit.get("entity", {}).get("summary", ""),
                            "content_link": hit.get("entity", {}).get("content_link", ""),
                            "content_type": hit.get("entity", {}).get("content_type", ""),
                            "source_book": hit.get("entity", {}).get("source_book", ""),
                            "source_page": hit.get("entity", {}).get("source_page", 0),
                            "quality_score": hit.get("entity", {}).get("quality_score", 0.0)
                        }
                    })
            
            return search_results
        except Exception as e:
            self.logger.error(f"搜索向量失败: {e}")
            return []

# 全局向量存储实例
vector_storage = VectorStorage() if MILVUS_LITE_AVAILABLE else None

def store_vectors(vectors: List[List[float]], metadata: List[Dict]) -> None:
    """存储向量到Milvus Lite"""
    if vector_storage:
        vector_storage.store_vectors(vectors, metadata)

def search_vectors(query_vector: List[float], top_k: int = 5) -> List[Dict]:
    """搜索向量"""
    if vector_storage:
        return vector_storage.search_vectors(query_vector, top_k)
    return []