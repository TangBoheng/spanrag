"""
向量化模块
生成摘要向量并存储到Milvus
"""
from typing import Dict, List, Any
from src.models.embedding_model import get_text_embedding
from src.utils.logger import setup_logger

class Vectorizer:
    """向量化器"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
    
    def create_embeddings(self, texts: List[str], model_config: Dict[str, Any] = None) -> List[List[float]]:
        """创建文本嵌入向量"""
        if not texts:
            return []
        
        embeddings = []
        for text in texts:
            try:
                embedding = get_text_embedding(text, model_config)
                embeddings.append(embedding)
            except Exception as e:
                self.logger.error(f"生成嵌入向量失败: {e}")
                # 添加零向量作为占位符
                embeddings.append([0.0] * 1024)  # 假设1024维向量
        
        return embeddings
    
    def create_vector_index(self, summaries: List[Dict], content_links: List[str]) -> List[Dict]:
        """创建向量索引"""
        if not summaries or not content_links:
            return []
        
        # 提取摘要文本
        summary_texts = [summary.get("summary", "") for summary in summaries]
        
        # 生成嵌入向量
        embeddings = self.create_embeddings(summary_texts)
        
        # 构建索引数据
        index_data = []
        for i, (summary, content_link, embedding) in enumerate(zip(summaries, content_links, embeddings)):
            index_data.append({
                "id": f"vector_{i}",
                "vector": embedding,
                "metadata": {
                    "summary": summary.get("summary", ""),
                    "content_link": content_link,
                    "content_type": summary.get("content_type", "text"),
                    "source_file": summary.get("source_file", ""),
                    "source_book": summary.get("source_book", ""),
                    "quality_score": summary.get("quality_score", 1.0)
                }
            })
        
        return index_data
