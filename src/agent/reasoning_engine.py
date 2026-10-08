"""
推理引擎
执行多步迭代推理
"""
from typing import Dict, List, Any
import json
from src.models.text_model import call_text_model
from src.models.multimodal_model import call_multimodal_model
from src.retrieval.content_fetcher import fetch_content_by_link
from src.utils.logger import setup_logger

class ReasoningEngine:
    """推理引擎"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
    
    def multi_modal_reasoning(self, summary: str, full_content: Any, query: str, model_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        多模态推理处理
        
        Args:
            summary (str): 内容摘要
            full_content (Any): 完整内容
            query (str): 用户查询
            model_config (Dict[str, Any]): 模型配置
        
        Returns:
            Dict[str, Any]: 推理结果
                {
                    "answer": str,              # 推理答案
                    "needs_iteration": bool,    # 是否需要迭代
                    "sub_question": str,        # 子问题（如果需要迭代）
                    "confidence": float,        # 置信度
                    "reasoning_steps": List[str] # 推理步骤
                }
        """
        try:
            # 构造推理提示
            if isinstance(full_content, dict) and "image_path" in full_content:
                # 图像内容
                prompt = f"""
                基于以下图像内容和用户查询进行推理：
                
                查询: {query}
                
                图像描述: {summary}
                
                请分析图像内容并回答查询。如果无法直接回答，请提出一个具体的子问题以便进一步检索相关信息。
                
                回答格式：
                {{
                    "answer": "直接回答或说明无法直接回答",
                    "needs_iteration": true/false,
                    "sub_question": "如果需要迭代，请提供具体的子问题",
                    "confidence": 0.0-1.0,
                    "reasoning_steps": ["步骤1", "步骤2"]
                }}
                """
                
                # 调用多模态模型
                response = call_multimodal_model(
                    text=prompt,
                    image_path=full_content["image_path"],
                    model_config=model_config
                )
            else:
                # 文本内容
                content_text = full_content if isinstance(full_content, str) else str(full_content)
                
                prompt = f"""
                基于以下内容和用户查询进行推理：
                
                查询: {query}
                
                内容摘要: {summary}
                
                完整内容:
                {content_text[:4000]}  # 限制长度
                
                请分析内容并回答查询。如果无法直接回答，请提出一个具体的子问题以便进一步检索相关信息。
                
                回答格式：
                {{
                    "answer": "直接回答或说明无法直接回答",
                    "needs_iteration": true/false,
                    "sub_question": "如果需要迭代，请提供具体的子问题",
                    "confidence": 0.0-1.0,
                    "reasoning_steps": ["步骤1", "步骤2"]
                }}
                """
                
                # 调用文本模型
                response = call_text_model(prompt, model_config=model_config)
            
            # 解析响应
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # 如果解析失败，构造默认响应
                result = {
                    "answer": response,
                    "needs_iteration": False,
                    "sub_question": "",
                    "confidence": 0.5,
                    "reasoning_steps": ["基于内容进行推理"]
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"多模态推理失败: {e}")
            return {
                "answer": "推理过程出现错误",
                "needs_iteration": False,
                "sub_question": "",
                "confidence": 0.0,
                "reasoning_steps": [f"错误: {str(e)}"]
            }
    
    def validate_answer(self, answer: str, query: str) -> bool:
        """
        验证答案是否完整回答了查询
        
        Args:
            answer (str): 生成的答案
            query (str): 原始查询
        
        Returns:
            bool: 答案是否完整
        """
        # 简单验证：答案不为空且不是错误信息
        if not answer or "错误" in answer or "无法" in answer:
            return False
        return True

# 全局推理引擎实例
reasoning_engine = ReasoningEngine()
