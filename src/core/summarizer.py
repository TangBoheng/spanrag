"""
摘要生成模块
支持文本和多模态摘要，带缓存和成本优化
"""
import hashlib
from typing import Dict, Any, List
from datetime import datetime
from src.models.text_model import call_text_model
from src.models.multimodal_model import call_multimodal_model
# from src.storage.content_storage import content_storage
from src.utils.logger import setup_logger

class Summarizer:
    """摘要生成器"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.summary_cache = {}  # 简化的缓存实现
    
    def generate_text_summary(self, content: str, content_id: str, model_type: str = "text") -> Dict[str, Any]:
        """生成文本摘要"""
        # 检查缓存
        cache_key = hashlib.md5(f"{content_id}_{model_type}".encode()).hexdigest()
        if cache_key in self.summary_cache:
            self.logger.info(f"从缓存获取摘要: {content_id}")
            return self.summary_cache[cache_key]
        
        start_time = datetime.now()
        
        # 构造提示词
        prompt = f"""
        请为以下内容生成简洁的摘要：
        
        {content[:4000]}  # 限制长度
        
        摘要要求：
        1. 保留关键信息
        2. 简洁明了
        3. 不超过200字
        """
        
        try:
            # 调用文本模型生成摘要
            summary = call_text_model(prompt, model_type=model_type)
            
            result = {
                "summary": summary,
                "content_id": content_id,
                "model_used": model_type,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "cache_hit": False
            }
            
            # 缓存结果
            self.summary_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            self.logger.error(f"生成文本摘要失败: {e}")
            raise
    
    def generate_multimodal_summary(self, content_type: str, content: Any, content_id: str) -> Dict[str, Any]:
        """生成多模态摘要（图像/表格）"""
        start_time = datetime.now()
        
        try:
            if content_type == "image":
                # 对于图像，调用多模态模型生成描述
                summary = call_multimodal_model(
                    text="请描述这张图片的内容，重点关注其中的信息和数据。",
                    image_path=content.get("image_path") if isinstance(content, dict) else content
                )
            elif content_type == "table":
                # 对于表格，提取关键信息生成摘要
                if isinstance(content, dict) and "table_data" in content:
                    table_text = self._table_to_text(content["table_data"])
                else:
                    table_text = str(content)
                
                prompt = f"""
                请为以下表格数据生成摘要：
                
                {table_text[:2000]}
                
                摘要要求：
                1. 说明表格的主要内容
                2. 提取关键数据点
                3. 不超过150字
                """
                summary = call_text_model(prompt)
            else:
                raise ValueError(f"不支持的内容类型: {content_type}")
            
            return {
                "summary": summary,
                "content_id": content_id,
                "content_type": content_type,
                "model_used": "multimodal",
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "cache_hit": False
            }
            
        except Exception as e:
            self.logger.error(f"生成多模态摘要失败: {e}")
            raise
    
    def _table_to_text(self, table_data: List[List[str]]) -> str:
        """将表格数据转换为文本"""
        if not table_data:
            return ""
        
        # 简单的表格转文本
        text_lines = []
        for row in table_data:
            text_lines.append(" | ".join(str(cell) for cell in row))
        
        return "\n".join(text_lines)
