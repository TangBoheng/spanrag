"""
内容获取器
获取完整内容并处理失败情况
"""
from typing import Dict, List, Any
import time
from src.storage.content_storage import content_storage
from src.utils.logger import setup_logger

class ContentFetchError(Exception):
    """内容获取错误"""
    pass

class ContentFetcher:
    """内容获取器"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.max_retries = 3
        self.retry_delay = 1  # 秒
    
    def fetch_content(self, content_link: str, max_retries: int = None) -> Dict:
        """
        获取内容
        
        Args:
            content_link (str): 内容链接
            max_retries (int): 最大重试次数
        
        Returns:
            Dict: 内容数据
        
        Raises:
            ContentFetchError: 内容获取失败
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        for attempt in range(max_retries + 1):
            try:
                # 解析内容链接
                content_data = content_storage.get_content(content_link)
                
                if not content_data:
                    raise ContentFetchError(f"未找到内容: {content_link}")
                
                self.logger.info(f"成功获取内容: {content_link}")
                return content_data
                
            except Exception as e:
                if attempt < max_retries:
                    self.logger.warning(f"获取内容失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}")
                    time.sleep(self.retry_delay * (2 ** attempt))  # 指数退避
                else:
                    self.logger.error(f"获取内容最终失败: {e}")
                    raise ContentFetchError(f"获取内容失败: {e}")
    
    def batch_fetch_contents(self, content_links: List[str]) -> List[Dict]:
        """
        批量获取内容
        
        Args:
            content_links (List[str]): 内容链接列表
        
        Returns:
            List[Dict]: 内容数据列表
        """
        contents = []
        failed_links = []
        
        for link in content_links:
            try:
                content = self.fetch_content(link)
                contents.append(content)
            except ContentFetchError as e:
                self.logger.error(f"批量获取内容失败: {link} - {e}")
                failed_links.append(link)
        
        if failed_links:
            self.logger.warning(f"批量获取内容中有 {len(failed_links)} 个失败")
        
        return contents

# 全局内容获取器实例
content_fetcher = ContentFetcher()

def fetch_content_by_link(content_link: str) -> Any:
    """
    根据链接获取内容
    
    Args:
        content_link (str): 内容链接
    
    Returns:
        Any: 内容数据
    """
    return content_fetcher.fetch_content(content_link)

def batch_fetch_contents(content_links: List[str]) -> List[Any]:
    """
    批量获取内容
    
    Args:
        content_links (List[str]): 内容链接列表
    
    Returns:
        List[Any]: 内容数据列表
    """
    return content_fetcher.batch_fetch_contents(content_links)
