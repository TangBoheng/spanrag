"""
答案生成器
生成最终格式化的答案
"""
from typing import Dict, List, Any
from datetime import datetime

class AnswerGenerator:
    """答案生成器"""
    
    def generate_final_answer(self, iteration_results: List[Dict[str, Any]], original_query: str) -> str:
        """
        基于迭代结果生成最终答案
        
        Args:
            iteration_results (List[Dict[str, Any]]): 迭代结果列表
            original_query (str): 原始查询
        
        Returns:
            str: 最终答案
        """
        if not iteration_results:
            return "抱歉，无法找到相关信息来回答您的问题。"
        
        # 获取最后一次迭代的结果
        last_iteration = iteration_results[-1]
        final_result = last_iteration["result"]
        
        answer = final_result.get("answer", "无答案")
        confidence = final_result.get("confidence", 0.0)
        
        # 添加置信度信息
        if confidence < 0.3:
            answer = f"【低置信度】{answer}"
        elif confidence < 0.6:
            answer = f"【中等置信度】{answer}"
        
        return answer
    
    def format_answer_with_sources(self, answer: str, source_metadatas: List[Dict]) -> str:
        """
        格式化答案并添加来源引用
        
        Args:
            answer (str): 答案文本
            source_metadatas (List[Dict]): 来源元数据列表，每个字典包含：
                - source_book: 来源书籍
                - source_page: 页码
                - book_author: 作者（可选）
                - publish_year: 出版年份（可选）
                - quality_score: 质量评分
        
        Returns:
            str: 格式化后的答案，包含来源引用
        """
        if not source_metadatas:
            return answer
        
        # 格式化答案
        formatted_answer = answer
        
        # 添加来源信息
        sources_text = "\n\n参考资料：\n"
        unique_sources = {}  # 去重
        
        for i, meta in enumerate(source_metadatas, 1):
            source_key = f"{meta.get('source_book', '未知书籍')}_{meta.get('source_page', 0)}"
            if source_key not in unique_sources:
                unique_sources[source_key] = {
                    "book": meta.get('source_book', '未知书籍'),
                    "page": meta.get('source_page', 0),
                    "author": meta.get('book_author', ''),
                    "year": meta.get('publish_year', ''),
                    "quality": meta.get('quality_score', 1.0)
                }
        
        for i, source in enumerate(unique_sources.values(), 1):
            source_line = f"{i}. {source['book']}"
            if source['author']:
                source_line += f" - {source['author']}"
            if source['year']:
                source_line += f" ({source['year']})"
            if source['page']:
                source_line += f", 第{source['page']}页"
            sources_text += source_line + "\n"
        
        return formatted_answer + sources_text

# 全局答案生成器实例
answer_generator = AnswerGenerator()

def generate_final_answer(iteration_results: List[Dict[str, Any]], original_query: str) -> str:
    """
    基于迭代结果生成最终答案
    
    Args:
        iteration_results (List[Dict[str, Any]]): 迭代结果列表
        original_query (str): 原始查询
    
    Returns:
        str: 最终答案
    """
    return answer_generator.generate_final_answer(iteration_results, original_query)

def format_answer_with_sources(answer: str, source_links: List[str]) -> str:
    """
    格式化答案并添加来源引用
    
    Args:
        answer (str): 答案文本
        source_links (List[str]): 来源链接列表
    
    Returns:
        str: 格式化后的答案
    """
    # 简化实现，实际应用中需要从链接解析元数据
    if not source_links:
        return answer
    
    sources_text = "\n\n参考资料：\n"
    for i, link in enumerate(source_links[:5], 1):  # 限制显示前5个来源
        sources_text += f"{i}. {link}\n"
    
    return answer + sources_text
