"""
存储模块测试
"""
import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.content_storage import ContentStorage

class TestContentStorage(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        # 创建临时目录用于测试
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test.db")
        self.content_storage = ContentStorage(self.db_path)
    
    def tearDown(self):
        """测试后清理"""
        # 清理临时目录
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_init_db(self):
        """测试数据库初始化"""
        # 检查表是否存在
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查文本内容表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='text_content'")
        self.assertIsNotNone(cursor.fetchone())
        
        # 检查图像内容表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='image_content'")
        self.assertIsNotNone(cursor.fetchone())
        
        # 检查表格内容表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='table_content'")
        self.assertIsNotNone(cursor.fetchone())
        
        conn.close()
    
    def test_save_text_content_success(self):
        """测试保存文本内容成功"""
        content = "Test content"
        metadata = {
            "source_book": "test_book.pdf",
            "source_page": 1
        }
        
        content_id = self.content_storage.save_text_content(content, metadata)
        
        self.assertTrue(content_id.startswith("text_"))
        
        # 验证内容是否正确保存
        result = self.content_storage.get_content(content_id)
        self.assertEqual(result["content"], content)
        self.assertIn("metadata", result)
    
    def test_save_text_content_missing_required_fields(self):
        """测试缺少必需字段"""
        content = "Test content"
        metadata = {
            "source_book": "test_book.pdf"
            # 缺少 source_page
        }
        
        with self.assertRaises(ValueError):
            self.content_storage.save_text_content(content, metadata)
    
    def test_get_content_not_found(self):
        """测试获取不存在的内容"""
        result = self.content_storage.get_content("nonexistent_id")
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()
