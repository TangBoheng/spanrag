"""
索引生成模块
管理Milvus集合和索引
"""
from typing import Dict, List, Any
from src.storage.vector_storage import store_vectors
from src.utils.logger import setup_logger

class Indexer:
    """索引生成器"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
    
    def create_text_index(self, summary: str, content_link: str, embedding: List[float]) -> bool:
        """创建文本索引"""
        try:
            metadata = [{
                "summary": summary,
                "content_link": content_link,
                "content_type": "text"
            }]
            
            vectors = [embedding]
            store_vectors(vectors, metadata)
            return True
        except Exception as e:
            self.logger.error(f"创建文本索引失败: {e}")
            return False
    
    def create_multimodal_index(self, summary: str, content_link: str, content_type: str, embedding: List[float]) -> bool:
        """创建多模态索引"""
        try:
            metadata = [{
                "summary": summary,
                "content_link": content_link,
                "content_type": content_type
            }]
            
            vectors = [embedding]
            store_vectors(vectors, metadata)
            return True
        except Exception as e:
            self.logger.error(f"创建多模态索引失败: {e}")
            return False
