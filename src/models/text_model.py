"""
文本模型接口模块
提供统一的文本模型调用接口，使用OpenAI兼容SDK
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
    print("警告: openai未安装，模型功能将不可用")

logger = setup_logger(__name__)

def call_text_model(prompt: str, model_config: Optional[Dict[str, Any]] = None, model_type: str = "text") -> str:
    """
    调用文本模型，使用OpenAI兼容SDK
    
    Args:
        prompt (str): 输入提示
        model_config (Optional[Dict[str, Any]]): 模型配置
        model_type (str): 模型类型 ('text', 'vision')
    
    Returns:
        str: 模型响应
    """
    if model_config is None:
        # 获取默认配置
        model_config = api_config.get_api_params(model_type)
    
    api_key = model_config.get("api_key", "")
    base_url = model_config.get("base_url", "https://api.openai.com/v1")
    model_name = model_config.get("model_name", "gpt-4")
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
        
        # 调用Chat Completions API
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return completion.choices[0].message.content.strip()
            
    except Exception as e:
        logger.error(f"调用文本模型失败: {e}")
        raise

def call_embedding_model(texts: list, model_config: Optional[Dict[str, Any]] = None) -> list:
    """
    调用嵌入模型，使用OpenAI兼容SDK
    
    Args:
        texts (list): 文本列表
        model_config (Optional[Dict[str, Any]]): 模型配置
    
    Returns:
        list: 嵌入向量列表
    """
    if model_config is None:
        model_config = api_config.get_api_params("embedding")
    
    api_key = model_config.get("api_key", "")
    base_url = model_config.get("base_url", "https://api.openai.com/v1")
    model_name = model_config.get("model_name", "text-embedding-ada-002")
    
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
        
        # 调用Embeddings API
        response = client.embeddings.create(
            model=model_name,
            input=texts,
            encoding_format="float"
        )
        
        return [data.embedding for data in response.data]
        
    except Exception as e:
        logger.error(f"调用嵌入模型失败: {e}")
        raise