"""
迭代控制器
管理多步迭代推理过程
"""
from typing import Dict, List, Any
from datetime import datetime
from src.retrieval.search_engine import search_by_query
from src.retrieval.content_fetcher import fetch_content_by_link
from src.agent.reasoning_engine import reasoning_engine
from src.utils.logger import setup_logger

class IterationController:
    """迭代控制器"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
    
    def should_continue_iteration(self, iteration_result: Dict[str, Any], max_iterations: int = 5, current_iteration: int = 0) -> bool:
        """
        判断是否需要继续迭代
        
        Args:
            iteration_result (Dict[str, Any]): 当前迭代结果
            max_iterations (int): 最大迭代次数，默认5
            current_iteration (int): 当前迭代次数
        
        Returns:
            bool: 是否继续迭代
        """
        # 检查是否达到最大迭代次数
        if current_iteration >= max_iterations:
            self.logger.info(f"达到最大迭代次数 {max_iterations}")
            return False
        
        # 检查是否需要迭代
        needs_iteration = iteration_result.get("needs_iteration", False)
        sub_question = iteration_result.get("sub_question", "").strip()
        
        if not needs_iteration or not sub_question:
            return False
        
        # 检查置信度
        confidence = iteration_result.get("confidence", 0.0)
        if confidence >= 0.8:  # 高置信度，不需要继续迭代
            return False
        
        return True
    
    def execute_iteration_cycle(self, initial_query: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        执行完整的迭代循环
        
        Args:
            initial_query (str): 初始查询
            max_iterations (int): 最大迭代次数，默认5
        
        Returns:
            Dict[str, Any]: 最终结果
        """
        iteration_results = []
        current_query = initial_query
        source_links = []
        
        for i in range(max_iterations):
            self.logger.info(f"执行第 {i+1} 次迭代，查询: {current_query}")
            
            # 1. 检索相关内容
            search_results = search_by_query(current_query, top_k=3)
            if not search_results:
                self.logger.warning("未找到相关结果")
                break
            
            # 2. 获取完整内容
            content_data_list = []
            for result in search_results:
                content_link = result["content_link"]
                try:
                    content_data = fetch_content_by_link(content_link)
                    content_data_list.append({
                        "summary": result["summary"],
                        "content": content_data,
                        "metadata": result["metadata"]
                    })
                    source_links.append(content_link)
                except Exception as e:
                    self.logger.error(f"获取内容失败: {content_link} - {e}")
            
            if not content_data_list:
                self.logger.warning("无法获取任何内容")
                break
            
            # 3. 进行推理
            best_result = None
            best_confidence = 0.0
            
            for content_data in content_data_list:
                reasoning_result = reasoning_engine.multi_modal_reasoning(
                    summary=content_data["summary"],
                    full_content=content_data["content"],
                    query=current_query
                )
                
                confidence = reasoning_result.get("confidence", 0.0)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_result = reasoning_result
            
            if not best_result:
                self.logger.warning("推理失败")
                break
            
            # 保存迭代结果
            iteration_results.append({
                "iteration": i + 1,
                "query": current_query,
                "result": best_result,
                "timestamp": datetime.now().isoformat()
            })
            
            # 4. 检查是否需要继续迭代
            if not self.should_continue_iteration(best_result, max_iterations, i + 1):
                self.logger.info("迭代终止条件满足")
                break
            
            # 5. 更新查询为子问题
            current_query = best_result.get("sub_question", current_query)
        
        # 生成最终答案
        final_answer = self._generate_final_answer(iteration_results, initial_query)
        
        return {
            "final_answer": final_answer,
            "iterations": iteration_results,
            "source_links": source_links,
            "total_iterations": len(iteration_results)
        }
    
    def _generate_final_answer(self, iteration_results: List[Dict], original_query: str) -> str:
        """生成最终答案"""
        if not iteration_results:
            return "无法生成答案"
        
        # 使用最后一次迭代的结果作为最终答案
        last_result = iteration_results[-1]["result"]
        answer = last_result.get("answer", "无答案")
        
        # 如果答案置信度低，添加警告
        confidence = last_result.get("confidence", 0.0)
        if confidence < 0.5:
            answer = f"[低置信度] {answer}"
        
        return answer

# 全局迭代控制器实例
iteration_controller = IterationController()
