"""
多模态模型接口模块
提供统一的多模态模型调用接口，使用OpenAI兼容SDK
"""
import os
from typing import Dict, Any, Optional
from config.api_config import api_config
from src.utils.logger import setup_logger

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("警告: openai未安装，多模态模型功能将不可用")

logger = setup_logger(__name__)

def call_multimodal_model(text: str, image_path: Optional[str] = None, 
                         table_data: Optional[list] = None, 
                         model_config: Optional[Dict[str, Any]] = None) -> str:
    """
    调用多模态模型，使用OpenAI兼容SDK
    
    Args:
        text (str): 文本内容
        image_path (str, optional): 图像路径
        table_data (list, optional): 表格数据
        model_config (Dict[str, Any]): 模型配置
    
    Returns:
        str: 模型响应
    """
    if model_config is None:
        model_config = api_config.get_api_params("vision")
    
    api_key = model_config.get("api_key", "")
    base_url = model_config.get("base_url", "https://api.openai.com/v1")
    model_name = model_config.get("model_name", "gpt-4-vision")
    temperature = model_config.get("temperature", 0.7)
    max_tokens = model_config.get("max_tokens", 2000)
    
    if not api_key:
        raise ValueError("API密钥未配置")
    
    if not OPENAI_AVAILABLE:
        raise ImportError("OpenAI SDK未安装")
    
    try:
        # 创建OpenAI客户端
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # 构造消息内容
        content = [{"type": "text", "text": text}]
        
        # 如果有图像，添加图像内容
        if image_path:
            # 这里需要实现图像编码或URL处理
            # 简化实现：使用文本描述代替
            content.append({"type": "text", "text": f"图像路径: {image_path}"})
        
        # 调用Chat Completions API
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return completion.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"调用多模态模型失败: {e}")
        raise