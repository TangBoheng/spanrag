"""
摘要生成器测试
"""
import unittest
import os
import sys
from unittest.mock import patch

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.summarizer import Summarizer

class TestSummarizer(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.summarizer = Summarizer()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.summarizer.summary_cache)
    
    @patch('src.core.summarizer.call_text_model')
    def test_generate_text_summary_success(self, mock_call_text_model):
        """测试文本摘要生成成功"""
        mock_call_text_model.return_value = "This is a summary."
        
        result = self.summarizer.generate_text_summary("Test content", "test_id")
        
        self.assertIn("summary", result)
        self.assertIn("content_id", result)
        self.assertEqual(result["summary"], "This is a summary.")
        self.assertEqual(result["content_id"], "test_id")
    
    def test_table_to_text_empty(self):
        """测试空表格转换"""
        result = self.summarizer._table_to_text([])
        self.assertEqual(result, "")
    
    def test_table_to_text_with_data(self):
        """测试表格转换"""
        table_data = [
            ["Name", "Age"],
            ["Alice", "25"],
            ["Bob", "30"]
        ]
        
        result = self.summarizer._table_to_text(table_data)
        expected = "Name | Age\nAlice | 25\nBob | 30"
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
