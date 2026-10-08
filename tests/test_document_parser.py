"""
文档解析器测试
"""
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.document_parser import DocumentParser

class TestDocumentParser(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.parser = DocumentParser()
    
    def test_init_default_engines(self):
        """测试默认OCR引擎初始化"""
        # 测试默认引擎设置
        self.assertIn("tesseract", self.parser.ocr_engines)
    
    def test_validate_ocr_engines(self):
        """测试OCR引擎验证"""
        # 测试有效引擎
        valid_engines = self.parser._validate_ocr_engines(["paddleocr", "tesseract"])
        self.assertIn("tesseract", valid_engines)
    
    @patch('src.core.document_parser.fitz.open')
    def test_parse_pdf_file_not_found(self, mock_fitz_open):
        """测试PDF文件不存在的情况"""
        mock_fitz_open.side_effect = FileNotFoundError("File not found")
        
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_pdf("nonexistent.pdf")
    
    @patch('src.core.document_parser.fitz.open')
    def test_parse_pdf_success(self, mock_fitz_open):
        """测试PDF解析成功"""
        # 模拟fitz文档对象
        mock_doc = MagicMock()
        mock_doc.__len__ = MagicMock(return_value=1)
        mock_doc.__enter__ = MagicMock(return_value=mock_doc)
        mock_doc.__exit__ = MagicMock(return_value=None)
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Test content"
        mock_page.get_images.return_value = []
        mock_doc.__getitem__ = MagicMock(return_value=mock_page)
        mock_fitz_open.return_value = mock_doc
        
        result = self.parser.parse_pdf("test.pdf")
        
        self.assertIn("text", result)
        self.assertIn("images", result)
        self.assertIn("tables", result)
        self.assertIn("metadata", result)
        self.assertEqual(result["metadata"]["total_pages"], 1)

if __name__ == '__main__':
    unittest.main()
