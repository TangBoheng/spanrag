"""
API配置管理模块
管理多供应商API密钥和参数，支持密钥轮换和负载均衡
"""
import json
import os
from typing import Dict, Any, List
from .settings import get_settings

class APIConfig:
    """API配置类，管理AI服务提供商配置"""
    
    def __init__(self):
        """初始化API配置"""
        self.settings = get_settings()
        self.providers = ["openai", "qwen", "anthropic", "custom"]
        self.rate_limits = {
            "openai": 1000,
            "qwen": 500,
            "anthropic": 800,
            "custom": 1000
        }
        self.fallback_chain = ["qwen","openai", "anthropic"]
    
    def get_api_params(self, model_type: str, provider: str = None) -> Dict[str, Any]:
        """获取指定模型类型的API参数"""
        config_data = self.settings.config_data
        model_config = config_data.get("model_config", {})
        
        # 根据模型类型选择模型名称
        model_mapping = {
            "text": model_config.get("text_model", "gpt-4"),
            "vision": model_config.get("vision_model", "gpt-4-vision"),
            "embedding": model_config.get("embedding_model", "text-embedding-ada-002")
        }
        
        # 选择提供商
        if not provider:
            provider = self.fallback_chain[0]  # 默认使用第一个提供商
        
        # 获取提供商配置
        provider_config = self.settings.get_api_config(provider)
        
        return {
            "api_key": provider_config.get("api_key", ""),
            "base_url": provider_config.get("base_url", "https://api.openai.com/v1"),
            "model_name": model_mapping.get(model_type, model_mapping["text"]),
            "temperature": model_config.get("temperature", 0.7),
            "max_tokens": model_config.get("max_tokens", 2000),
            "timeout": 30,
            "retry_attempts": 3
        }
    
    def _get_base_url(self, provider: str) -> str:
        """获取提供商的基础URL"""
        provider_config = self.settings.get_api_config(provider)
        return provider_config.get("base_url", "https://api.openai.com/v1")
    
    def rotate_key(self, provider: str) -> bool:
        """轮换指定供应商的API密钥"""
        # 这里可以实现密钥轮换逻辑
        # 例如从密钥管理系统获取新密钥
        return True

# 全局API配置实例
api_config = APIConfig()
