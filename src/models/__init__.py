"""
模型接口模块
提供统一的模型调用接口
"""
from .text_model import call_text_model
from .multimodal_model import call_multimodal_model
from .embedding_model import get_text_embedding

__all__ = [
    "call_text_model",
    "call_multimodal_model",
    "get_text_embedding"
]
