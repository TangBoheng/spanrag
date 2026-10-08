#!/usr/bin/env python3
"""
数据验证工具
验证处理后的数据完整性、质量和一致性
"""
import argparse
import os
import sys
import json
import sqlite3
from typing import Dict, List, Tuple
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.content_storage import CONTENT_METADATA_SCHEMA
from src.utils.logger import setup_logger

logger = setup_logger(__name__, log_file="logs/data_validator.log")

class DataValidator:
    def __init__(self, db_path: str = "data/content.db"):
        self.db_path = db_path
        self.validation_results = {
            "content_integrity": {},
            "metadata_quality": {},
            "vector_index": {},
            "statistics": {}
        }
    
    def validate_content_integrity(self) -> Dict[str, any]:
        """验证内容完整性"""
        results = {
            "total_records": 0,
            "valid_records": 0,
            "invalid_records": 0,
            "missing_content": [],
            "empty_content": []
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查文本内容表
            cursor.execute("SELECT COUNT(*) FROM text_content")
            total_text = cursor.fetchone()[0]
            results["total_records"] += total_text
            
            # 检查空内容
            cursor.execute("SELECT id FROM text_content WHERE content IS NULL OR content = ''")
            empty_content = cursor.fetchall()
            results["empty_content"] = [row[0] for row in empty_content]
            
            # 检查缺失内容
            cursor.execute("SELECT id FROM text_content WHERE content IS NULL")
            missing_content = cursor.fetchall()
            results["missing_content"] = [row[0] for row in missing_content]
            
            # 计算有效记录数
            results["valid_records"] = total_text - len(results["empty_content"]) - len(results["missing_content"])
            results["invalid_records"] = len(results["empty_content"]) + len(results["missing_content"])
            
            conn.close()
            
        except Exception as e:
            logger.error(f"验证内容完整性失败: {e}")
            results["error"] = str(e)
        
        return results
    
    def validate_metadata_quality(self) -> Dict[str, any]:
        """验证元数据质量"""
        results = {
            "total_records": 0,
            "complete_metadata": 0,
            "incomplete_metadata": 0,
            "missing_fields": {},
            "quality_scores": {
                "high": 0,  # > 0.8
                "medium": 0,  # 0.5-0.8
                "low": 0  # < 0.5
            }
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取所有记录
            cursor.execute("SELECT id, metadata FROM text_content")
            records = cursor.fetchall()
            results["total_records"] = len(records)
            
            required_fields = ["source_book", "source_page", "content_hash", "content_type"]
            
            for record_id, metadata_str in records:
                try:
                    metadata = json.loads(metadata_str) if metadata_str else {}
                    results["complete_metadata"] += 1
                    
                    # 检查必需字段
                    missing_fields = [field for field in required_fields if field not in metadata]
                    if missing_fields:
                        results["incomplete_metadata"] += 1
                        for field in missing_fields:
                            results["missing_fields"][field] = results["missing_fields"].get(field, 0) + 1
                    
                    # 检查质量评分
                    quality_score = metadata.get("quality_score", 0.0)
                    if quality_score > 0.8:
                        results["quality_scores"]["high"] += 1
                    elif quality_score > 0.5:
                        results["quality_scores"]["medium"] += 1
                    else:
                        results["quality_scores"]["low"] += 1
                        
                except json.JSONDecodeError:
                    results["incomplete_metadata"] += 1
                    results["missing_fields"]["metadata_parsing"] = results["missing_fields"].get("metadata_parsing", 0) + 1
            
            conn.close()
            
        except Exception as e:
            logger.error(f"验证元数据质量失败: {e}")
            results["error"] = str(e)
        
        return results
    
    def validate_vector_index(self) -> Dict[str, any]:
        """验证向量索引"""
        results = {
            "vector_storage_available": False,
            "collection_exists": False,
            "index_count": 0,
            "dimension_check": True
        }
        
        try:
            # 检查Milvus连接
            from src.storage.vector_storage import MILVUS_AVAILABLE, vector_storage
            results["vector_storage_available"] = MILVUS_AVAILABLE
            
            if MILVUS_AVAILABLE and vector_storage:
                results["collection_exists"] = True
                # 这里可以添加更多向量索引的验证逻辑
                # 例如检查索引数量、维度等
                
        except Exception as e:
            logger.error(f"验证向量索引失败: {e}")
            results["error"] = str(e)
        
        return results
    
    def generate_statistics(self) -> Dict[str, any]:
        """生成数据统计信息"""
        stats = {
            "content_size_distribution": {},
            "source_book_distribution": {},
            "processing_time_stats": {}
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 内容大小分布
            cursor.execute("SELECT LENGTH(content) FROM text_content")
            content_lengths = [row[0] for row in cursor.fetchall() if row[0] is not None]
            if content_lengths:
                stats["content_size_distribution"] = {
                    "min": min(content_lengths),
                    "max": max(content_lengths),
                    "avg": sum(content_lengths) / len(content_lengths),
                    "total": sum(content_lengths)
                }
            
            # 来源书籍分布
            cursor.execute("SELECT metadata FROM text_content")
            metadata_records = cursor.fetchall()
            source_books = {}
            processing_times = []
            
            for metadata_str, in metadata_records:
                try:
                    metadata = json.loads(metadata_str) if metadata_str else {}
                    source_book = metadata.get("source_book", "unknown")
                    source_books[source_book] = source_books.get(source_book, 0) + 1
                    
                    processing_time = metadata.get("processing_time")
                    if processing_time is not None:
                        processing_times.append(processing_time)
                except json.JSONDecodeError:
                    pass
            
            stats["source_book_distribution"] = source_books
            
            if processing_times:
                stats["processing_time_stats"] = {
                    "min": min(processing_times),
                    "max": max(processing_times),
                    "avg": sum(processing_times) / len(processing_times)
                }
            
            conn.close()
            
        except Exception as e:
            logger.error(f"生成统计数据失败: {e}")
            stats["error"] = str(e)
        
        return stats
    
    def run_validation(self) -> Dict[str, any]:
        """运行完整的数据验证"""
        logger.info("开始数据验证src..")
        
        # 验证内容完整性
        self.validation_results["content_integrity"] = self.validate_content_integrity()
        
        # 验证元数据质量
        self.validation_results["metadata_quality"] = self.validate_metadata_quality()
        
        # 验证向量索引
        self.validation_results["vector_index"] = self.validate_vector_index()
        
        # 生成统计数据
        self.validation_results["statistics"] = self.generate_statistics()
        
        logger.info("数据验证完成")
        return self.validation_results
    
    def generate_report(self) -> str:
        """生成验证报告"""
        report = []
        report.append("=" * 50)
        report.append("数据验证报告")
        report.append("=" * 50)
        
        # 内容完整性
        integrity = self.validation_results["content_integrity"]
        report.append("\n1. 内容完整性:")
        report.append(f"   总记录数: {integrity.get('total_records', 0)}")
        report.append(f"   有效记录: {integrity.get('valid_records', 0)}")
        report.append(f"   无效记录: {integrity.get('invalid_records', 0)}")
        if integrity.get('empty_content'):
            report.append(f"   空内容记录: {len(integrity['empty_content'])}")
        if integrity.get('missing_content'):
            report.append(f"   缺失内容记录: {len(integrity['missing_content'])}")
        
        # 元数据质量
        metadata = self.validation_results["metadata_quality"]
        report.append("\n2. 元数据质量:")
        report.append(f"   总记录数: {metadata.get('total_records', 0)}")
        report.append(f"   完整元数据: {metadata.get('complete_metadata', 0)}")
        report.append(f"   不完整元数据: {metadata.get('incomplete_metadata', 0)}")
        if metadata.get('missing_fields'):
            report.append("   缺失字段:")
            for field, count in metadata['missing_fields'].items():
                report.append(f"     {field}: {count}")
        
        quality_scores = metadata.get('quality_scores', {})
        report.append("   质量评分分布:")
        report.append(f"     高质量 (>0.8): {quality_scores.get('high', 0)}")
        report.append(f"     中等质量 (0.5-0.8): {quality_scores.get('medium', 0)}")
        report.append(f"     低质量 (<0.5): {quality_scores.get('low', 0)}")
        
        # 向量索引
        vector_index = self.validation_results["vector_index"]
        report.append("\n3. 向量索引:")
        report.append(f"   向量存储可用: {vector_index.get('vector_storage_available', False)}")
        report.append(f"   集合存在: {vector_index.get('collection_exists', False)}")
        report.append(f"   索引数量: {vector_index.get('index_count', 0)}")
        
        # 统计数据
        stats = self.validation_results["statistics"]
        report.append("\n4. 统计数据:")
        size_dist = stats.get("content_size_distribution", {})
        if size_dist:
            report.append("   内容大小分布:")
            report.append(f"     最小: {size_dist.get('min', 0)} 字符")
            report.append(f"     最大: {size_dist.get('max', 0)} 字符")
            report.append(f"     平均: {size_dist.get('avg', 0):.2f} 字符")
        
        source_dist = stats.get("source_book_distribution", {})
        if source_dist:
            report.append("   来源书籍分布:")
            for book, count in sorted(source_dist.items(), key=lambda x: x[1], reverse=True)[:5]:
                report.append(f"     {book}: {count}")
        
        time_stats = stats.get("processing_time_stats", {})
        if time_stats:
            report.append("   处理时间统计:")
            report.append(f"     最短: {time_stats.get('min', 0):.2f} 秒")
            report.append(f"     最长: {time_stats.get('max', 0):.2f} 秒")
            report.append(f"     平均: {time_stats.get('avg', 0):.2f} 秒")
        
        report.append("\n" + "=" * 50)
        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="数据验证工具")
    parser.add_argument("--db-path", default="data/content.db", help="数据库路径")
    parser.add_argument("--output", default="validation_report.txt", help="输出报告文件")
    parser.add_argument("--json-output", default="validation_results.json", help="JSON格式输出文件")
    
    args = parser.parse_args()
    
    # 确保日志目录存在
    os.makedirs("logs", exist_ok=True)
    
    # 创建验证器
    validator = DataValidator(args.db_path)
    
    # 运行验证
    results = validator.run_validation()
    
    # 生成报告
    report = validator.generate_report()
    
    # 保存报告
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 保存JSON结果
    with open(args.json_output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    print(report)
    print(f"\n详细报告已保存到: {args.output}")
    print(f"JSON结果已保存到: {args.json_output}")

if __name__ == "__main__":
    main()
