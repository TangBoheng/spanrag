#!/usr/bin/env python3
"""
读取Milvus Lite数据库中特定ID的摘要内容
"""

import sys
import os
from pymilvus import MilvusClient

def read_document_by_id(db_path: str, collection_name: str, doc_id: int):
    """读取指定ID的文档数据"""
    try:
        # 连接到Milvus Lite
        client = MilvusClient(uri=db_path)
        
        # 查询指定ID的数据
        result = client.get(
            collection_name=collection_name,
            ids=[doc_id]
        )
        
        if result:
            doc_data = result[0]
            print(f"=== 文档 ID: {doc_id} ===")
            print(f"摘要: {doc_data.get('summary', '')}")
            print(f"内容链接: {doc_data.get('content_link', '')}")
            print(f"内容类型: {doc_data.get('content_type', '')}")
            print(f"来源书籍: {doc_data.get('source_book', '')}")
            print(f"页码: {doc_data.get('source_page', '')}")
            print(f"质量评分: {doc_data.get('quality_score', '')}")
            print(f"提取日期: {doc_data.get('extraction_date', '')}")
            print(f"向量维度: {len(doc_data.get('vector', []))}")
        else:
            print(f"未找到ID为 {doc_id} 的文档")
            
    except Exception as e:
        print(f"读取失败: {e}")

def list_all_documents(db_path: str, collection_name: str):
    """列出所有文档的ID和摘要"""
    try:
        client = MilvusClient(uri=db_path)
        
        # 获取集合信息
        info = client.describe_collection(collection_name)
        print(f"集合信息: {info}")
        
        # 查询所有文档（限制数量避免内存问题）
        results = client.query(
            collection_name=collection_name,
            filter="",  # 空过滤器获取所有
            limit=100,
            output_fields=["id", "summary", "source_book"]
        )
        
        print(f"\n=== 文档列表 (共{len(results)}个) ===")
        for doc in results:
            print(f"ID: {doc['id']}, 书籍: {doc.get('source_book', '')}")
            print(f"  摘要: {doc.get('summary', '')[:100]}...")
            print()
            
    except Exception as e:
        print(f"列出文档失败: {e}")

if __name__ == "__main__":
    # 默认路径，根据您的实际情况调整
    DB_PATH = "./data/milvus_lite.db"
    COLLECTION_NAME = "rag_documents"
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            list_all_documents(DB_PATH, COLLECTION_NAME)
        else:
            doc_id = int(sys.argv[1])
            read_document_by_id(DB_PATH, COLLECTION_NAME, doc_id)
    else:
        print("用法:")
        print("  python read_milvus.py <文档ID>    # 读取特定文档")
        print("  python read_milvus.py list        # 列出所有文档")