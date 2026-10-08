"""
PDF文档解析模块
支持多OCR引擎、图像预处理和内容质量评估
"""
import fitz  # PyMuPDF
try:
    import camelot
    import pandas as pd
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False
    print("警告: camelot未安装，表格提取功能将不可用")
try:
    import paddleocr
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from typing import Dict, List, Any, Tuple
import os
from datetime import datetime
import hashlib
from src.utils.logger import setup_logger

class DocumentParser:
    def __init__(self, ocr_engines: List[str] = None):
        self.ocr_engines = self._validate_ocr_engines(ocr_engines or ["paddleocr", "tesseract"])
        self.logger = setup_logger(__name__)
    
    def _validate_ocr_engines(self, engines: List[str]) -> List[str]:
        """验证并过滤可用的OCR引擎"""
        available_engines = []
        for engine in engines:
            if engine == "paddleocr" and PADDLEOCR_AVAILABLE:
                available_engines.append(engine)
            elif engine == "tesseract" and TESSERACT_AVAILABLE:
                available_engines.append(engine)
            elif engine == "easyocr":
                available_engines.append(engine)
        return available_engines or ["tesseract"]  # 默认使用tesseract
    
    def parse_pdf(self, file_path: str) -> Dict[str, List[Dict]]:
        """解析PDF文件，提取文本、图像和表格内容"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF文件不存在: {file_path}")
        
        start_time = datetime.now()
        result = {
            "text": [],
            "images": [],
            "tables": [],
            "metadata": {
                "file_path": file_path,
                "source_book": os.path.basename(file_path),
                "extraction_date": datetime.now().isoformat(),
                "quality_scores": {}
            }
        }
        
        try:
            with fitz.open(file_path) as doc:
                result["metadata"]["total_pages"] = len(doc)
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    page_result = self._process_page(page, page_num, file_path)
                    result["text"].extend(page_result["text"])
                    result["images"].extend(page_result["images"])
                    result["tables"].extend(page_result["tables"])
                    
                result["metadata"]["processing_time"] = (datetime.now() - start_time).total_seconds()
                result["metadata"]["engines_used"] = self.ocr_engines
                
        except Exception as e:
            self.logger.error(f"PDF解析失败: {e}")
            raise RuntimeError(f"PDF处理失败: {e}")
        
        return result
    
    def _process_page(self, page, page_num: int, file_path: str) -> Dict[str, List]:
        """处理单个PDF页面"""
        page_text = []
        page_images = []
        page_tables = []
        
        # 1. 直接提取文本
        text_content = page.get_text()
        if text_content.strip():
            page_text.append({
                "page": page_num,
                "content": text_content,
                "bbox": page.rect,
                "font_info": {},
                "confidence": 1.0,
                "engine_used": "direct_extraction",
                "quality_score": 1.0
            })
        
        # 2. 如果文本内容少或需要OCR，进行图像OCR
        if len(text_content) < 100:  # 文本太少，进行OCR
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            img = Image.frombytes("RGB", [pix.width, pix.height], img_data)
            
            ocr_result = self._extract_text_with_ocr(img)
            if ocr_result["text"].strip():
                page_text.append({
                    "page": page_num,
                    "content": ocr_result["text"],
                    "bbox": page.rect,
                    "font_info": {},
                    "confidence": ocr_result["confidence"],
                    "engine_used": ocr_result["engine_used"],
                    "quality_score": ocr_result["confidence"]
                })
        
        # 3. 提取图像
        image_list = page.get_images()
        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            base_image = page.parent.extract_image(xref)
            if base_image:
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # 保存图像文件
                image_dir = "data/extracted_content/images"
                os.makedirs(image_dir, exist_ok=True)
                image_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}_p{page_num}_i{img_index}.{image_ext}"
                image_path = os.path.join(image_dir, image_filename)
                
                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                page_images.append({
                    "page": page_num,
                    "image_path": image_path,
                    "bbox": [0, 0, base_image["width"], base_image["height"]],
                    "width": base_image["width"],
                    "height": base_image["height"],
                    "format": image_ext,
                    "quality": "original"
                })

        if CAMELOT_AVAILABLE:
            try:
                # 将PDF页面保存为临时文件供camelot处理
                temp_pdf_path = f"/tmp/page_{page_num}.pdf"
                temp_doc = fitz.open()
                temp_doc.insert_pdf(page.parent, from_page=page_num, to_page=page_num)
                temp_doc.save(temp_pdf_path)
                temp_doc.close()
                
                # 使用camelot提取表格
                tables = camelot.read_pdf(temp_pdf_path, pages="1", flavor="lattice",line_scale=40)
                
                for table_index, table in enumerate(tables):
                    if table.parsing_report['accuracy'] > 80:  # 准确率阈值
                        table_data = table.df.values.tolist()  # 转换为列表
                        
                        page_tables.append({
                            "page": page_num,
                            "table_index": table_index,
                            "table_data": table_data,
                            "accuracy": table.parsing_report['accuracy'],
                            "bbox": table._bbox,
                            "engine_used": "camelot"
                        })
                        
                        # 可选：保存表格为CSV文件
                        # table_dir = "data/extracted_content/tables"
                        # os.makedirs(table_dir, exist_ok=True)
                        # table_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}_p{page_num}_t{table_index}.csv"
                        # table_path = os.path.join(table_dir, table_filename)
                        # table.df.to_csv(table_path, index=False, encoding='utf-8')
                
                # 清理临时文件
                os.remove(temp_pdf_path)
                
            except Exception as e:
                self.logger.warning(f"表格提取失败: {e}")

        print("page_images",page_images)
        print("page_text",page_text)
        print("page_tables",page_tables)
        
        return {"text": page_text, "images": page_images, "tables": page_tables}
    
    def _extract_text_with_ocr(self, page_image: Image.Image) -> Dict[str, Any]:
        """对PDF页面进行OCR提取，支持多引擎备降"""
        best_result = {"text": "", "confidence": 0.0, "engine_used": "none"}
        
        for engine in self.ocr_engines:
            try:
                if engine == "paddleocr" and PADDLEOCR_AVAILABLE:
                    result = self._paddle_ocr(page_image)
                elif engine == "tesseract" and TESSERACT_AVAILABLE:
                    result = self._tesseract_ocr(page_image)
                else:
                    continue
                
                if result["confidence"] > best_result["confidence"]:
                    best_result = result
                    
            except Exception as e:
                self.logger.warning(f"{engine} OCR失败: {e}")
                continue
        
        return best_result
    
    def _paddle_ocr(self, image: Image.Image) -> Dict[str, Any]:
        """使用PaddleOCR进行文字识别"""
        if not PADDLEOCR_AVAILABLE:
            return {"text": "", "confidence": 0.0, "engine_used": "paddleocr"}
        
        ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang='ch')
        img_array = np.array(image)
        result = ocr.ocr(img_array, cls=True)
        
        text_lines = []
        confidences = []
        
        if result and result[0]:
            for line in result[0]:
                if line and line[1]:
                    text_lines.append(line[1][0])
                    confidences.append(line[1][1])
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        return {
            "text": "\n".join(text_lines),
            "confidence": avg_confidence,
            "engine_used": "paddleocr"
        }
    
    def _tesseract_ocr(self, image: Image.Image) -> Dict[str, Any]:
        """使用Tesseract进行文字识别"""
        if not TESSERACT_AVAILABLE:
            return {"text": "", "confidence": 0.0, "engine_used": "tesseract"}
        
        # 图像预处理
        img = image.convert('L')  # 转灰度
        img = img.point(lambda x: 0 if x < 128 else 255, '1')  # 二值化
        
        # OCR识别
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,!?;:()[]{}<>-+*/=@#$%^&_|"\''
        text = pytesseract.image_to_string(img, config=custom_config)
        
        # 获取置信度（需要额外调用）
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        confidences = [float(conf) for conf in data['conf'] if float(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "text": text,
            "confidence": avg_confidence,
            "engine_used": "tesseract"
        }
