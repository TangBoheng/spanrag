"""
项目全局配置管理模块
通过单例模式提供配置访问，支持环境变量覆盖
"""
import os
import json
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class Settings:
    """项目配置类，管理所有运行时参数"""
    
    def __init__(self, config_file: str = "config/settings.json"):
        """初始化配置，加载配置文件并验证"""
        self.config_file = config_file
        self.config_data = self.load_config()
        self.validate()
    
    def load_config(self) -> Dict[str, Any]:
        """从配置文件加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        except FileNotFoundError:
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "api_config": {
                "openai": {
                    "api_key": os.getenv("OPENAI_API_KEY", ""),
                    "base_url": "https://api.openai.com/v1"
                },
                "qwen": {
                    "api_key": os.getenv("QWEN_API_KEY", ""),
                    "base_url": "https://dashscope.aliyuncs.com/api/v1"
                },
                "anthropic": {
                    "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
                    "base_url": "https://api.anthropic.com/v1"
                },
                "custom": {
                    "api_key": "",
                    "base_url": ""
                }
            },
            "milvus_config": {
                "host": "localhost",
                "port": 19530,
                "collection_name": "rag_documents",
                "user": "",
                "password": "",
                "secure": False
            },
            "model_config": {
                "text_model": "gpt-4",
                "vision_model": "gpt-4-vision",
                "embedding_model": "text-embedding-ada-002",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "processing_config": {
                "chunk_size": 1000,
                "overlap_size": 100,
                "max_iterations": 5,
                "ocr_engines": ["paddleocr", "tesseract", "easyocr"]
            },
            "continuity_factors": {
                "font_similarity": 0.3,
                "line_spacing": 0.2,
                "text_alignment": 0.2,
                "semantic_continuity": 0.3
            },
            "merge_threshold": 0.7,
            "termination_conditions": {
                "answer_completeness": 0.8,
                "confidence_threshold": 0.7,
                "max_iterations": 5,
                "information_gain": 0.1,
                "query_specificity": 0.6
            }
        }
    
    def validate(self) -> bool:
        """验证配置完整性"""
        required_sections = ["api_config", "milvus_config", "model_config", "processing_config"]
        return all(section in self.config_data for section in required_sections)
    
    def get_api_config(self, provider: str = "openai") -> Dict[str, str]:
        """获取指定提供商的API配置"""
        return self.config_data["api_config"].get(provider, {
            "api_key": "",
            "base_url": "https://api.openai.com/v1"
        })
    
    def get_ocr_engines(self) -> List[str]:
        """获取OCR引擎优先级列表"""
        return self.config_data["processing_config"].get("ocr_engines", ["paddleocr", "tesseract"])
    
    def get_continuity_factors(self) -> Dict[str, float]:
        """获取段落连续性检测权重"""
        return self.config_data.get("continuity_factors", {})
    
    def get_merge_threshold(self) -> float:
        """获取段落合并置信度阈值"""
        return self.config_data.get("merge_threshold", 0.7)
    
    def get_iteration_conditions(self) -> Dict[str, float]:
        """获取迭代终止条件"""
        return self.config_data.get("termination_conditions", {})

def get_settings() -> Settings:
    """获取全局配置实例"""
    return Settings()
