"""
内容提取器测试
"""
import unittest
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.content_extractor import ContentExtractor

class TestContentExtractor(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.extractor = ContentExtractor()
    
    def test_extract_text_chunks_empty_input(self):
        """测试空输入"""
        result = self.extractor.extract_text_chunks([])
        self.assertEqual(result, [])
    
    def test_extract_text_chunks_single_chunk(self):
        """测试单个文本块提取"""
        text_data = [{
            "content": "This is a test paragraph.",
            "page": 1,
            "source_file": "test.pdf"
        }]
        
        result = self.extractor.extract_text_chunks(text_data)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["content"], "This is a test paragraph.")
        self.assertIn("metadata", result[0])
    
    def test_remove_duplicates(self):
        """测试去重功能"""
        chunks = [
            {"content": "Same content", "metadata": {"hash": "abc123"}},
            {"content": "Same content", "metadata": {"hash": "abc123"}},
            {"content": "Different content", "metadata": {"hash": "def456"}}
        ]
        
        result = self.extractor.remove_duplicates(chunks)
        
        # 应该只保留两个不同的块（去重后）
        self.assertEqual(len(result), 2)

if __name__ == '__main__':
    unittest.main()
