"""
Milvus数据库配置模块
管理向量数据库连接和集合配置，支持分区和索引优化
"""
from typing import Dict, Any
from .settings import get_settings

class MilvusConfig:
    """Milvus配置类"""
    
    def __init__(self):
        """初始化Milvus配置"""
        settings = get_settings().config_data
        self.milvus_config = settings.get("milvus_config", {})
    
    def get_connection_params(self) -> Dict[str, Any]:
        """获取Milvus连接参数"""
        # 对于Milvus Lite，只返回必要的参数
        return {
            "uri": self.milvus_config.get("uri", "sqlite:///data/milvus_lite.db"),
            "collection_name": self.milvus_config.get("collection_name", "rag_documents")
        }
    
    def get_collection_config(self) -> Dict[str, Any]:
        """获取集合配置"""
        return {
            "collection_name": self.milvus_config.get("collection_name", "rag_documents"),
            "dimension": 1024,  # 默认嵌入维度
            "metric_type": "IP",  # 内积相似度
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128},
            "partition_by_type": True
        }
    
    def get_index_config(self) -> Dict[str, Any]:
        """获取索引配置"""
        return {
            "index_type": "IVF_FLAT",
            "metric_type": "IP",
            "params": {"nlist": 128}
        }