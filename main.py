"""
主程序入口
协调各个模块，提供命令行接口
"""
import argparse
import os
import sys
from typing import Dict, Any
from src.core.document_parser import DocumentParser
from src.core.content_extractor import ContentExtractor
from src.core.paragraph_merger import ParagraphMerger
from src.core.summarizer import Summarizer
from src.core.vectorizer import Vectorizer
from src.storage.content_storage import content_storage
from src.storage.vector_storage import store_vectors
from src.agent.iteration_controller import iteration_controller
from src.utils.logger import setup_logger
from src.utils.filter import is_likely_real_table
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger = setup_logger(__name__)


def process_pdf(pdf_path: str, output_dir: str = "data/processed") -> bool:
    try:
        logger.info(f"开始处理PDF文件: {pdf_path}")
        
        # 1. 解析PDF
        parser = DocumentParser()
        parsed_data = parser.parse_pdf(pdf_path)
        
        # 2. 初始化组件
        extractor = ContentExtractor()
        merger = ParagraphMerger()
        summarizer = Summarizer()
        vectorizer = Vectorizer()
        
        all_summaries = []
        all_content_links = []
        
        # 3. 处理图像内容
        for image_info in parsed_data["images"]:
            image_metadata = {
                "source_book": os.path.basename(pdf_path),
                "source_page": image_info["page"],
                "image_format": image_info["format"],
                "width": image_info["width"],
                "height": image_info["height"],
                "quality": image_info["quality"]
            }
            
            # 保存图像内容
            content_id = content_storage.save_image_content(
                image_info["image_path"],
                image_metadata
            )
            
            # 生成图像摘要
            summary_result = summarizer.generate_multimodal_summary(
                content_type="image",
                content=image_info,  # 传递整个图像信息字典
                content_id=content_id
            )
            
            all_summaries.append({
                "summary": summary_result["summary"],
                "source_book": os.path.basename(pdf_path),
                "source_page": image_info["page"],
                "quality_score": 1.0,
                "content_type": "image"
            })
            all_content_links.append(f"image://{content_id}")
            
            logger.info(f"图像内容处理完成: {content_id}")
        
        # 4. 处理表格内容
        filtered_tables = []
        for table_info in parsed_data["tables"]:
            if is_likely_real_table(table_info["table_data"]):
                filtered_tables.append(table_info)
            else:
                logger.debug(f"过滤疑似误识别表格: page={table_info['page']}, data={table_info['table_data']}")
        
        for table_info in filtered_tables:
            table_metadata = {
                "source_book": os.path.basename(pdf_path),
                "source_page": table_info["page"],
                "accuracy": table_info.get("accuracy", 0),
                "engine_used": table_info.get("engine_used", "camelot")
            }
            
            # 保存表格内容
            content_id = content_storage.save_table_content(
                table_info["table_data"],
                table_metadata
            )
            
            # 生成表格摘要
            summary_result = summarizer.generate_multimodal_summary(
                content_type="table",
                content={"table_data": table_info["table_data"]},  # 传递表格数据
                content_id=content_id
            )
            
            all_summaries.append({
                "summary": summary_result["summary"],
                "source_book": os.path.basename(pdf_path),
                "source_page": table_info["page"],
                "quality_score": table_info.get("accuracy", 0) / 100.0,
                "content_type": "table"
            })
            all_content_links.append(f"table://{content_id}")
            
            logger.info(f"表格内容处理完成: {content_id}")
        
        # 5. 处理文本内容
        text_chunks = extractor.extract_text_chunks(parsed_data["text"])
        merged_chunks = merger.merge_paragraphs(text_chunks)
        
        for i, chunk in enumerate(merged_chunks):
            # 生成文本摘要
            summary_result = summarizer.generate_text_summary(
                chunk["content"], 
                f"chunk_{i}"
            )
            
            # 保存文本内容
            content_id = content_storage.save_text_content(
                chunk["content"],
                chunk["metadata"]
            )
            
            all_summaries.append({
                "summary": summary_result["summary"],
                "source_book": os.path.basename(pdf_path),
                "source_page": chunk["metadata"].get("source_page", 0),
                "quality_score": summary_result.get("quality_score", 1.0),
                "content_type": "text"
            })
            all_content_links.append(f"text://{content_id}")
        
        # 6. 创建向量索引和存储向量
        vector_data = vectorizer.create_vector_index(all_summaries, all_content_links)
        vectors = [item["vector"] for item in vector_data]
        metadata = [item["metadata"] for item in vector_data]
        store_vectors(vectors, metadata)
        
        logger.info(f"PDF文件处理完成: {pdf_path}")
        return True
        
    except Exception as e:
        logger.error(f"处理PDF文件失败: {e}")
        return False



def query(question: str, max_iterations: int = 5) -> str:
    """
    查询问答
    
    Args:
        question (str): 用户问题
        max_iterations (int): 最大迭代次数
    
    Returns:
        str: 答案
    """
    try:
        logger.info(f"开始查询: {question}")
        
        # 执行迭代推理
        result = iteration_controller.execute_iteration_cycle(
            question, 
            max_iterations
        )
        
        logger.info("查询完成")
        return result["final_answer"]
        
    except Exception as e:
        logger.error(f"查询失败: {e}")
        return f"查询失败: {e}"

def batch_process(pdf_directory: str) -> bool:
    """
    批量处理PDF文件
    
    Args:
        pdf_directory (str): PDF文件目录
    
    Returns:
        bool: 处理是否成功
    """
    try:
        logger.info(f"开始批量处理目录: {pdf_directory}")
        
        # 获取所有PDF文件
        pdf_files = [f for f in os.listdir(pdf_directory) 
                    if f.lower().endswith('.pdf')]
        
        success_count = 0
        for pdf_file in pdf_files:
            pdf_path = os.path.join(pdf_directory, pdf_file)
            if process_pdf(pdf_path):
                success_count += 1
                logger.info(f"处理成功: {pdf_file}")
            else:
                logger.error(f"处理失败: {pdf_file}")
        
        logger.info(f"批量处理完成，成功处理 {success_count}/{len(pdf_files)} 个文件")
        return success_count == len(pdf_files)
        
    except Exception as e:
        logger.error(f"批量处理失败: {e}")
        return False

def main() -> None:
    """
    主函数，处理命令行参数并启动服务
    
    支持的命令：
    - process_pdf: 处理PDF文件
    - query: 查询问答
    - batch_process: 批量处理
    """
    parser = argparse.ArgumentParser(
        prog="quaestor",
        description="Quaestor - 智能 Agentic RAG 框架：PDF 文档多步迭代问答",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 处理PDF命令
    process_parser = subparsers.add_parser("process_pdf", help="处理PDF文件")
    process_parser.add_argument("pdf_path", help="PDF文件路径")
    process_parser.add_argument("--output_dir", default="data/processed", 
                              help="输出目录")
    
    # 查询命令
    query_parser = subparsers.add_parser("query", help="查询问答")
    query_parser.add_argument("question", help="用户问题")
    query_parser.add_argument("--max_iterations", type=int, default=5,
                             help="最大迭代次数")
    
    # 批量处理命令
    batch_parser = subparsers.add_parser("batch_process", help="批量处理")
    batch_parser.add_argument("pdf_directory", help="PDF文件目录")
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 执行相应命令
    if args.command == "process_pdf":
        process_pdf(args.pdf_path, args.output_dir)
    elif args.command == "query":
        answer = query(args.question, args.max_iterations)
        print(f"答案: {answer}")
    elif args.command == "batch_process":
        batch_process(args.pdf_directory)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()


