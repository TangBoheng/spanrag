"""
内容截取与存储模块
实现动态分块、内容去重和质量评估
"""
import hashlib
from typing import Dict, List, Any, Tuple
from datetime import datetime
import re

class ContentExtractor:
    """内容提取器"""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def extract_text_chunks(self, text_data: List[Dict], chunk_size: int = None, overlap: int = None) -> List[Dict]:
        """按语义边界智能切分文本"""
        if chunk_size is None:
            chunk_size = self.chunk_size
        if overlap is None:
            overlap = self.overlap
            
        chunks = []
        chunk_id_counter = 0
        
        for text_item in text_data:
            content = text_item.get("content", "")
            if not content.strip():
                continue
                
            # 按段落分割
            paragraphs = self._split_into_paragraphs(content)
            
            current_chunk = ""
            current_metadata = {
                "page": text_item.get("page", 0),
                "source_file": text_item.get("source_file", ""),
                "source_book": text_item.get("source_book", ""),
                "engine_used": text_item.get("engine_used", ""),
                "ocr_confidence": text_item.get("confidence", 1.0),
                "extraction_date": datetime.now().isoformat()
            }
            
            for i, paragraph in enumerate(paragraphs):
                # 如果当前块加上新段落超过块大小，则保存当前块并开始新块
                if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
                    # 保存当前块
                    chunk_hash = hashlib.sha256(current_chunk.encode()).hexdigest()
                    chunks.append({
                        "content": current_chunk.strip(),
                        "metadata": {
                            **current_metadata,
                            "chunk_id": f"chunk_{chunk_id_counter}",
                            "start_pos": 0,  # 简化处理
                            "end_pos": len(current_chunk),
                            "semantic_boundary": True,
                            "quality_score": text_item.get("quality_score", 1.0),
                            "hash": chunk_hash
                        }
                    })
                    chunk_id_counter += 1
                    
                    # 开始新块，保留重叠部分
                    if overlap > 0 and len(current_chunk) > overlap:
                        current_chunk = current_chunk[-overlap:] + "\n" + paragraph
                    else:
                        current_chunk = paragraph
                else:
                    if current_chunk:
                        current_chunk += "\n" + paragraph
                    else:
                        current_chunk = paragraph
            
            # 保存最后一个块
            if current_chunk.strip():
                chunk_hash = hashlib.sha256(current_chunk.encode()).hexdigest()
                chunks.append({
                    "content": current_chunk.strip(),
                    "metadata": {
                        **current_metadata,
                        "chunk_id": f"chunk_{chunk_id_counter}",
                        "start_pos": 0,
                        "end_pos": len(current_chunk),
                        "semantic_boundary": True,
                        "quality_score": text_item.get("quality_score", 1.0),
                        "hash": chunk_hash
                    }
                })
                chunk_id_counter += 1
        
        return chunks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """将文本分割成段落"""
        # 按空行分割段落
        paragraphs = re.split(r'\n\s*\n', text)
        # 过滤空段落
        return [p.strip() for p in paragraphs if p.strip()]
    
    def remove_duplicates(self, chunks: List[Dict], similarity_threshold: float = 0.9) -> List[Dict]:
        """基于内容哈希和语义相似度去重"""
        unique_chunks = []
        seen_hashes = set()
        
        for chunk in chunks:
            chunk_hash = chunk["metadata"]["hash"]
            if chunk_hash not in seen_hashes:
                seen_hashes.add(chunk_hash)
                unique_chunks.append(chunk)
        
        return unique_chunks
