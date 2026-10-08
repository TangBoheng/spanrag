"""
文件操作工具模块
提供文件处理相关的工具函数
"""
import os
import hashlib
from typing import Union

def ensure_directory_exists(path: str) -> bool:
    """
    确保目录存在，不存在则创建
    
    Args:
        path (str): 目录路径
    
    Returns:
        bool: 操作成功标志
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录失败: {e}")
        return False

def get_file_hash(file_path: str) -> str:
    """
    获取文件哈希值（用于去重）
    
    Args:
        file_path (str): 文件路径
    
    Returns:
        str: 文件哈希值
    """
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"计算文件哈希失败: {e}")
        return ""

def get_file_size(file_path: str) -> int:
    """
    获取文件大小
    
    Args:
        file_path (str): 文件路径
    
    Returns:
        int: 文件大小（字节）
    """
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        print(f"获取文件大小失败: {e}")
        return 0
