"""
段落合并模块
实现跨页段落检测和智能合并
"""
from datetime import datetime
from typing import Dict, List, Any
import re
from src.utils.logger import setup_logger

class ParagraphMerger:
    """段落合并器"""
    
    def __init__(self, continuity_factors: Dict[str, float] = None, threshold: float = 0.7):
        self.continuity_factors = continuity_factors or {
            "font_similarity": 0.3,
            "line_spacing": 0.2,
            "text_alignment": 0.2,
            "semantic_continuity": 0.3
        }
        self.threshold = threshold
        self.logger = setup_logger(__name__)
    
    def detect_continuity(self, text_chunks: List[Dict]) -> List[Dict]:
        """检测文本块之间的连续性"""
        continuity_results = []
        
        for i in range(len(text_chunks) - 1):
            current_chunk = text_chunks[i]
            next_chunk = text_chunks[i + 1]
            
            # 计算连续性得分
            continuity_score = self._calculate_continuity_score(current_chunk, next_chunk)
            
            # 判断是否连续
            is_continued = continuity_score > self.threshold
            
            continuity_results.append({
                "chunk_id": current_chunk["metadata"]["chunk_id"],
                "is_continued": is_continued,
                "continuity_score": continuity_score,
                "factors": {
                    "font_similarity": 0.5,  # 简化实现
                    "line_spacing": 0.6,
                    "text_alignment": 0.7,
                    "semantic_continuity": 0.8
                }
            })
        
        return continuity_results
    
    def _calculate_continuity_score(self, chunk1: Dict, chunk2: Dict) -> float:
        """计算两个文本块的连续性得分"""
        # 简化实现：基于文本特征的启发式计算
        score = 0.0
        
        # 1. 字体相似度（简化）
        font_sim = 0.8 if chunk1.get("font_info") == chunk2.get("font_info") else 0.3
        score += self.continuity_factors["font_similarity"] * font_sim
        
        # 2. 行距一致性（简化）
        line_space_sim = 0.7  # 假设一致
        score += self.continuity_factors["line_spacing"] * line_space_sim
        
        # 3. 文本对齐方式（简化）
        alignment_sim = 0.8  # 假设一致
        score += self.continuity_factors["text_alignment"] * alignment_sim
        
        # 4. 语义连续性（简化）
        semantic_sim = self._calculate_semantic_similarity(chunk1["content"], chunk2["content"])
        score += self.continuity_factors["semantic_continuity"] * semantic_sim
        
        return min(1.0, score)  # 限制在0-1之间
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """计算语义相似度（简化实现）"""
        # 简化实现：基于关键词重叠
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def merge_paragraphs(self, text_chunks: List[Dict], threshold: float = None) -> List[Dict]:
        """合并具有高连续性的段落"""
        if threshold is None:
            threshold = self.threshold
            
        # 检测连续性
        continuity_results = self.detect_continuity(text_chunks)
        
        merged_chunks = []
        i = 0
        
        while i < len(text_chunks):
            current_chunk = text_chunks[i]
            
            # 检查是否有后续连续块需要合并
            merged_content = current_chunk["content"]
            merged_metadata = current_chunk["metadata"].copy()
            merged_pages = [current_chunk["metadata"].get("page", 0)]
            merged_bbox = [current_chunk["metadata"].get("bbox", [])]
            merged_chunks_list = [current_chunk["metadata"].get("chunk_id", "")]
            
            # 向后查找连续的块
            j = i
            while j < len(continuity_results) and j < len(text_chunks) - 1:
                continuity = continuity_results[j]
                if continuity["is_continued"] and continuity["continuity_score"] >= threshold:
                    j += 1
                    next_chunk = text_chunks[j]
                    merged_content += "\n" + next_chunk["content"]
                    merged_pages.append(next_chunk["metadata"].get("page", 0))
                    merged_bbox.append(next_chunk["metadata"].get("bbox", []))
                    merged_chunks_list.append(next_chunk["metadata"].get("chunk_id", ""))
                else:
                    break
            
            # 创建合并后的块
            merged_chunk = {
                "content": merged_content,
                "metadata": {
                    **merged_metadata,
                    "pages": merged_pages,
                    "bbox": merged_bbox,
                    "merged_chunks": merged_chunks_list,
                    "merge_date": datetime.now().isoformat()
                }
            }
            
            merged_chunks.append(merged_chunk)
            i = j + 1 if j > i else i + 1
        
        return merged_chunks
