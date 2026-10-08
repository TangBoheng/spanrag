"""
嵌入模型接口模块
提供统一的嵌入模型调用接口
"""
from typing import List, Any, Optional, Dict
from src.models.text_model import call_embedding_model
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def get_text_embedding(text: str, model_config: Optional[Dict[str, Any]] = None) -> List[float]:
    """
    获取文本嵌入向量
    
    Args:
        text (str): 输入文本
        model_config (Optional[Dict[str, Any]]): 模型配置
    
    Returns:
        List[float]: 嵌入向量
    """
    try:
        embeddings = call_embedding_model([text], model_config)
        return embeddings[0] if embeddings else []
    except Exception as e:
        logger.error(f"获取文本嵌入向量失败: {e}")
        # 返回零向量作为默认值
        return [0.0] * 1024

def get_multimodal_embedding(content_type: str, content: Any, 
                            model_config: Optional[Dict[str, Any]] = None) -> List[float]:
    """
    获取多模态嵌入向量
    
    Args:
        content_type (str): 内容类型
        content (Any): 内容数据
        model_config (Optional[Dict[str, Any]]): 模型配置
    
    Returns:
        List[float]: 嵌入向量
    """
    try:
        if content_type == "text":
            return get_text_embedding(str(content), model_config)
        elif content_type == "image":
            # 对于图像，可以提取描述然后获取嵌入
            # 这里简化处理，实际应用中可能需要更复杂的处理
            return get_text_embedding("图像内容", model_config)
        elif content_type == "table":
            # 对于表格，可以转换为文本然后获取嵌入
            if isinstance(content, dict) and "table_data" in content:
                table_text = "\n".join([" | ".join(str(cell) for cell in row) 
                                      for row in content["table_data"]])
            else:
                table_text = str(content)
            return get_text_embedding(table_text, model_config)
        else:
            logger.warning(f"不支持的内容类型: {content_type}")
            return [0.0] * 1024
    except Exception as e:
        logger.error(f"获取多模态嵌入向量失败: {e}")
        return [0.0] * 1024

