#!/usr/bin/env python3
"""
批量处理脚本
支持并行处理、进度跟踪和错误恢复
"""
import argparse
import os
import sys
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.document_parser import DocumentParser
from src.core.content_extractor import ContentExtractor
from src.core.paragraph_merger import ParagraphMerger
from src.core.summarizer import Summarizer
from src.core.vectorizer import Vectorizer
from src.storage.content_storage import content_storage
from src.storage.vector_storage import store_vectors
from src.utils.logger import setup_logger

logger = setup_logger(__name__, log_file="logs/batch_processor.log")

class BatchProcessor:
    def __init__(self, max_workers: int = 4, output_dir: str = "data/processed"):
        self.max_workers = max_workers
        self.output_dir = output_dir
        self.processed_files = set()
        self.failed_files = []
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "start_time": None,
            "end_time": None
        }
        
    def get_pdf_files(self, directory: str) -> List[str]:
        """获取目录中的所有PDF文件"""
        pdf_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        return pdf_files
    
    def process_single_file(self, pdf_path: str) -> Tuple[bool, str]:
        """处理单个PDF文件"""
        try:
            logger.info(f"开始处理文件: {pdf_path}")
            
            # 1. 解析PDF
            parser = DocumentParser()
            parsed_data = parser.parse_pdf(pdf_path)
            
            # 2. 提取内容块
            extractor = ContentExtractor()
            text_chunks = extractor.extract_text_chunks(parsed_data["text"])
            
            # 3. 合并段落
            merger = ParagraphMerger()
            merged_chunks = merger.merge_paragraphs(text_chunks)
            
            # 4. 生成摘要并存储
            summarizer = Summarizer()
            vectorizer = Vectorizer()
            
            summaries = []
            content_links = []
            
            for i, chunk in enumerate(merged_chunks):
                # 生成摘要
                summary_result = summarizer.generate_text_summary(
                    chunk["content"], 
                    f"chunk_{i}"
                )
                
                # 保存内容
                content_id = content_storage.save_text_content(
                    chunk["content"],
                    chunk["metadata"]
                )
                
                # 生成内容链接
                content_link = f"text://{content_id}"
                
                summaries.append(summary_result)
                content_links.append(content_link)
            
            # 5. 创建向量索引
            vector_data = vectorizer.create_vector_index(summaries, content_links)
            
            # 6. 存储向量
            vectors = [item["vector"] for item in vector_data]
            metadata = [item["metadata"] for item in vector_data]
            store_vectors(vectors, metadata)
            
            logger.info(f"文件处理完成: {pdf_path}")
            return True, pdf_path
            
        except Exception as e:
            logger.error(f"处理文件失败 {pdf_path}: {e}")
            return False, f"{pdf_path}: {str(e)}"
    
    def process_batch(self, pdf_directory: str) -> Dict[str, any]:
        """批量处理PDF文件"""
        self.stats["start_time"] = time.time()
        
        # 获取所有PDF文件
        pdf_files = self.get_pdf_files(pdf_directory)
        self.stats["total"] = len(pdf_files)
        
        logger.info(f"找到 {len(pdf_files)} 个PDF文件")
        
        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_file = {
                executor.submit(self.process_single_file, pdf_path): pdf_path 
                for pdf_path in pdf_files
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_file):
                try:
                    success, result = future.result()
                    if success:
                        self.stats["success"] += 1
                        self.processed_files.add(result)
                        logger.info(f"成功处理: {result}")
                    else:
                        self.stats["failed"] += 1
                        self.failed_files.append(result)
                        logger.error(f"处理失败: {result}")
                except Exception as e:
                    self.stats["failed"] += 1
                    pdf_path = future_to_file[future]
                    error_msg = f"{pdf_path}: {str(e)}"
                    self.failed_files.append(error_msg)
                    logger.error(f"处理异常 {pdf_path}: {e}")
        
        self.stats["end_time"] = time.time()
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, any]:
        """生成处理报告"""
        duration = self.stats["end_time"] - self.stats["start_time"] if self.stats["end_time"] else 0
        
        report = {
            "stats": self.stats,
            "processed_files": list(self.processed_files),
            "failed_files": self.failed_files,
            "duration": duration,
            "throughput": self.stats["total"] / duration if duration > 0 else 0
        }
        
        return report
    
    def save_report(self, report: Dict[str, any], output_file: str = "batch_report.json"):
        """保存处理报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"报告已保存到: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="批量处理PDF文件")
    parser.add_argument("pdf_directory", help="PDF文件目录")
    parser.add_argument("--max-workers", type=int, default=4, help="最大并发工作线程数")
    parser.add_argument("--output-dir", default="data/processed", help="输出目录")
    parser.add_argument("--report-file", default="batch_report.json", help="报告文件名")
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # 创建批量处理器
    processor = BatchProcessor(
        max_workers=args.max_workers,
        output_dir=args.output_dir
    )
    
    # 执行批量处理
    report = processor.process_batch(args.pdf_directory)
    
    # 保存报告
    processor.save_report(report, args.report_file)
    
    # 打印摘要
    print(f"批量处理完成:")
    print(f"  总文件数: {report['stats']['total']}")
    print(f"  成功处理: {report['stats']['success']}")
    print(f"  处理失败: {report['stats']['failed']}")
    print(f"  处理时间: {report['duration']:.2f} 秒")
    print(f"  处理速度: {report['throughput']:.2f} 文件/秒")
    
    if report['failed_files']:
        print(f"  失败文件:")
        for failed_file in report['failed_files']:
            print(f"    - {failed_file}")

if __name__ == "__main__":
    main()
