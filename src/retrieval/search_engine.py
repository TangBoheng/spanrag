"""
搜索引擎模块
执行查询和内容检索
"""
from typing import Dict, List, Any
import re
from src.storage.vector_storage import search_vectors
from src.models.embedding_model import get_text_embedding
from src.utils.logger import setup_logger

class SearchEngine:
    """搜索引擎"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        执行搜索查询
        
        Args:
            query (str): 用户查询
            top_k (int): 返回结果数量
        
        Returns:
            List[Dict]: 检索结果
                [
                    {
                        "summary": str,
                        "content_link": str,
                        "similarity": float,
                        "metadata": dict
                    }
                ]
        """
        try:
            # 预处理查询
            processed_query = self.preprocess_query(query)
            
            # 生成查询向量
            query_vector = get_text_embedding(processed_query)
            
            # 执行向量搜索
            vector_results = search_vectors(query_vector, top_k)
            
            # 格式化结果
            results = []
            for result in vector_results:
                results.append({
                    "summary": result["metadata"].get("summary", ""),
                    "content_link": result["metadata"].get("content_link", ""),
                    "similarity": result["distance"],
                    "metadata": {
                        "summary": result["metadata"].get("summary", ""),
                        "content_link": result["metadata"].get("content_link", ""),
                        "content_type": result["metadata"].get("content_type", "text"),
                        "source_book": result["metadata"].get("source_book", ""),
                        "source_page": result["metadata"].get("source_page", 0),
                        "quality_score": result["metadata"].get("quality_score", 1.0),
                        "similarity": result["distance"]
                    }
                })
            
            self.logger.info(f"搜索完成，返回 {len(results)} 个结果")
            return results
            
        except Exception as e:
            self.logger.error(f"搜索失败: {e}")
            return []
    
    def preprocess_query(self, query: str) -> str:
        """
        预处理查询
        
        Args:
            query (str): 用户查询
        
        Returns:
            str: 预处理后的查询
        """
        # 移除多余空格
        query = re.sub(r'\s+', ' ', query.strip())
        
        # 移除特殊字符（保留中英文、数字、常见标点）
        query = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()\-]', '', query)
        
        return query

# 全局搜索引擎实例
search_engine = SearchEngine()

def search_by_query(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    根据查询文本检索相似内容
    
    Args:
        query (str): 查询文本
        top_k (int): 返回结果数量，默认5
    
    Returns:
        List[Dict[str, Any]]: 检索结果列表
    """
    return search_engine.search(query, top_k)
