"""
Agent模块测试
"""
import unittest
import os
import sys
from unittest.mock import patch

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.reasoning_engine import ReasoningEngine
from src.agent.iteration_controller import IterationController
from src.agent.answer_generator import AnswerGenerator

class TestReasoningEngine(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.reasoning_engine = ReasoningEngine()
    
    def test_validate_answer_valid(self):
        """测试有效答案验证"""
        answer = "This is a valid answer."
        result = self.reasoning_engine.validate_answer(answer, "Test question")
        self.assertTrue(result)
    
    def test_validate_answer_invalid(self):
        """测试无效答案验证"""
        answer = "无法回答"
        result = self.reasoning_engine.validate_answer(answer, "Test question")
        self.assertFalse(result)

class TestIterationController(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.iteration_controller = IterationController()
    
    def test_should_continue_iteration_max_iterations(self):
        """测试达到最大迭代次数"""
        result = self.iteration_controller.should_continue_iteration(
            {"needs_iteration": True, "sub_question": "Test"},
            max_iterations=5,
            current_iteration=5
        )
        self.assertFalse(result)
    
    def test_should_continue_iteration_valid(self):
        """测试有效迭代条件"""
        result = self.iteration_controller.should_continue_iteration(
            {"needs_iteration": True, "sub_question": "Test", "confidence": 0.5},
            max_iterations=5,
            current_iteration=1
        )
        self.assertTrue(result)

class TestAnswerGenerator(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.answer_generator = AnswerGenerator()
    
    def test_generate_final_answer_empty(self):
        """测试空迭代结果"""
        result = self.answer_generator.generate_final_answer([], "Test question")
        self.assertEqual(result, "抱歉，无法找到相关信息来回答您的问题。")
    
    def test_format_answer_with_sources_empty(self):
        """测试空来源格式化"""
        result = self.answer_generator.format_answer_with_sources("Test answer", [])
        self.assertEqual(result, "Test answer")

if __name__ == '__main__':
    unittest.main()
