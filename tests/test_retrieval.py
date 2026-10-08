"""
检索模块测试
"""
import unittest
import os
import sys
from unittest.mock import patch

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieval.search_engine import SearchEngine
from src.retrieval.content_fetcher import ContentFetcher

class TestSearchEngine(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.search_engine = SearchEngine()
    
    def test_preprocess_query(self):
        """测试查询预处理"""
        query = "  This is a   test query!  "
        result = self.search_engine.preprocess_query(query)
        self.assertEqual(result, "This is a test query!")
    
    def test_preprocess_query_special_chars(self):
        """测试特殊字符处理"""
        query = "Test@#$%^&*()query"
        result = self.search_engine.preprocess_query(query)
        # 应该移除特殊字符，保留中英文和常见标点
        self.assertIn("Test", result)
        self.assertIn("query", result)

class TestContentFetcher(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.content_fetcher = ContentFetcher()
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.content_fetcher.max_retries, 3)
        self.assertEqual(self.content_fetcher.retry_delay, 1)

if __name__ == '__main__':
    unittest.main()
