"""
内容存储系统
管理文本、图像、表格内容的存储
"""
import os
import json
import sqlite3
from typing import Dict, Any, List
import hashlib
from datetime import datetime
from src.utils.logger import setup_logger

# 元数据模式定义
CONTENT_METADATA_SCHEMA = {
    "source_book": str,           # 来源书籍文件名
    "source_page": int,           # 原始页码
    "book_author": str,           # 作者信息
    "publish_year": int,          # 出版年份
    "quality_score": float,       # 内容质量评分 (0-1)
    "processing_time": float,     # 处理耗时(秒)
    "ocr_confidence": float,      # OCR置信度 (0-1)
    "content_hash": str,          # 内容哈希值 (SHA256)
    "chunk_id": str,              # 内容块ID
    "content_type": str,          # 内容类型 (text/image/table)
    "engine_used": str,           # 使用的OCR/处理引擎
    "file_path": str,             # 原始文件路径
    "extraction_date": str,       # 提取时间戳
    "version": int                # 元数据版本
}

class ContentStorage:
    """内容存储系统"""
    
    def __init__(self, db_path: str = "data/content.db"):
        self.db_path = db_path
        self.logger = setup_logger(__name__)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建文本内容表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS text_content (
                id TEXT PRIMARY KEY,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建图像内容表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_content (
                id TEXT PRIMARY KEY,
                image_path TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建表格内容表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS table_content (
                id TEXT PRIMARY KEY,
                table_data TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_text_content(self, content: str, metadata: Dict) -> str:
        """
        保存文本内容到数据库
        
        Args:
            content (str): 文本内容
            metadata (Dict): 元数据字典，应包含：
                - source_book: 来源书籍文件名
                - source_page: 原始页码
                - quality_score: 质量评分 (0-1)
                - content_hash: 内容哈希值
                - ocr_confidence: OCR置信度
                - engine_used: 使用的引擎
                - 其他CONTENT_METADATA_SCHEMA中的推荐字段
        
        Returns:
            str: 内容ID
        
        Raises:
            ValueError: 元数据缺少必需字段
            StorageError: 存储操作失败
        """
        # 验证必需字段，提供默认值
        required_fields = {
            "source_book": os.path.basename(metadata.get("file_path", "unknown.pdf")),
            "source_page": metadata.get("page", 0)  # 使用page字段作为source_page的默认值
        }
        
        # 确保必需字段存在
        for field, default_value in required_fields.items():
            if field not in metadata:
                metadata[field] = default_value
        
        # 生成内容ID
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        content_id = f"text_{content_hash[:16]}"
        
        # 添加默认元数据
        default_metadata = {
            "content_hash": content_hash,
            "content_type": "text",
            "created_at": datetime.now().isoformat()
        }
        metadata = {**default_metadata, **metadata}
        
        # 保存到数据库
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO text_content (id, content, metadata)
                VALUES (?, ?, ?)
            ''', (content_id, content, json.dumps(metadata)))
            conn.commit()
            conn.close()
            
            self.logger.info(f"文本内容保存成功: {content_id}")
            return content_id
        except Exception as e:
            self.logger.error(f"保存文本内容失败: {e}")
            raise Exception(f"存储操作失败: {e}")
    
    def save_image_content(self, image_path: str, metadata: Dict) -> str:
        """
        保存图像内容到文件系统
        
        Args:
            image_path (str): 图像文件路径
            metadata (Dict): 元数据字典，应包含：
                - source_book: 来源书籍文件名
                - source_page: 原始页码
                - quality_score: 图像质量评分 (0-1)
                - content_hash: 图像哈希值
                - image_format: 图像格式 (PNG/JPEG等)
                - resolution: 图像分辨率
                - file_path: 原始文件路径
                - extraction_date: 提取时间戳
        
        Returns:
            str: 内容ID
        
        Raises:
            ValueError: 元数据缺少必需字段
            StorageError: 存储操作失败
        """
        # 验证必需字段
        required_fields = ["source_book", "source_page"]
        for field in required_fields:
            if field not in metadata:
                raise ValueError(f"元数据缺少必需字段: {field}")
        
        # 生成内容ID
        with open(image_path, 'rb') as f:
            image_data = f.read()
            content_hash = hashlib.sha256(image_data).hexdigest()
        content_id = f"image_{content_hash[:16]}"
        
        # 添加默认元数据
        default_metadata = {
            "content_hash": content_hash,
            "content_type": "image",
            "created_at": datetime.now().isoformat()
        }
        metadata = {**default_metadata, **metadata}
        print("metadata",metadata)
        print("image_path",image_path)
        print("content_id",content_id)
        # 保存到数据库
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO image_content (id, image_path, metadata)
                VALUES (?, ?, ?)
            ''', (content_id, image_path, json.dumps(metadata)))
            conn.commit()
            conn.close()
            
            self.logger.info(f"图像内容保存成功: {content_id}")
            return content_id
        except Exception as e:
            self.logger.error(f"保存图像内容失败: {e}")
            raise Exception(f"存储操作失败: {e}")
    

    def save_table_content(self, table_data: List[List[str]], metadata: Dict) -> str:
        """
        保存表格内容到数据库
        
        Args:
            table_data (List[List[str]]): 表格数据（二维列表）
            metadata (Dict): 元数据字典，应包含：
                - source_book: 来源书籍文件名
                - source_page: 原始页码
                - accuracy: 识别准确率
                - engine_used: 使用的识别引擎
            
        Returns:
            str: 内容ID
            
        Raises:
            ValueError: 元数据缺少必需字段
            StorageError: 存储操作失败
        """
        # 验证必需字段
        required_fields = ["source_book", "source_page"]
        for field in required_fields:
            if field not in metadata:
                raise ValueError(f"元数据缺少必需字段: {field}")
        
        # 生成内容ID
        table_json = json.dumps(table_data)
        content_hash = hashlib.sha256(table_json.encode()).hexdigest()
        content_id = f"table_{content_hash[:16]}"
        
        # 添加默认元数据
        default_metadata = {
            "content_hash": content_hash,
            "content_type": "table",
            "created_at": datetime.now().isoformat()
        }
        metadata = {**default_metadata, **metadata}
        
        # 保存到数据库
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO table_content (id, table_data, metadata)
                VALUES (?, ?, ?)
            ''', (content_id, table_json, json.dumps(metadata)))
            conn.commit()
            conn.close()
            
            self.logger.info(f"表格内容保存成功: {content_id}")
            return content_id
            
        except Exception as e:
            self.logger.error(f"保存表格内容失败: {e}")
            raise Exception(f"存储操作失败: {e}")


    def get_content(self, content_id: str) -> Dict:
        """
        获取内容
        
        Args:
            content_id (str): 内容ID
        
        Returns:
            Dict: 内容数据
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 根据ID前缀确定表名
            if content_id.startswith("text_"):
                table = "text_content"
                cursor.execute(f'SELECT content, metadata FROM {table} WHERE id = ?', (content_id,))
                row = cursor.fetchone()
                if row:
                    content, metadata_str = row
                    return {
                        "content": content,
                        "metadata": json.loads(metadata_str) if metadata_str else {}
                    }
            elif content_id.startswith("image_"):
                table = "image_content"
                cursor.execute(f'SELECT image_path, metadata FROM {table} WHERE id = ?', (content_id,))
                row = cursor.fetchone()
                if row:
                    image_path, metadata_str = row
                    return {
                        "image_path": image_path,
                        "metadata": json.loads(metadata_str) if metadata_str else {}
                    }
            elif content_id.startswith("table_"):
                table = "table_content"
                cursor.execute(f'SELECT table_data, metadata FROM {table} WHERE id = ?', (content_id,))
                row = cursor.fetchone()
                if row:
                    table_data, metadata_str = row
                    return {
                        "table_data": json.loads(table_data) if table_data else [],
                        "metadata": json.loads(metadata_str) if metadata_str else {}
                    }
            
            conn.close()
            return {}
        except Exception as e:
            self.logger.error(f"获取内容失败: {e}")
            return {}

# 全局内容存储实例
content_storage = ContentStorage()
