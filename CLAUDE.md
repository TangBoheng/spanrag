# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

SpanRAG 是一个基于Python构建的智能Agentic RAG（检索增强生成）框架，专门用于处理PDF文档并执行多步迭代推理。该系统特别擅长处理扫描版和文字版PDF，使用OCR技术、自动段落合并和向量索引进行智能问答。

## 核心命令

### 开发和测试
```bash
# 安装依赖
pip install -r requirements.txt

# 运行所有测试
pytest tests/

# 运行特定测试模块
python -m pytest tests/test_document_parser.py -v

# 快速开发测试
python tests/quick_test.py
```

### 核心操作
```bash
# 处理单个PDF文件
python main.py process_pdf /path/to/document.pdf

# 查询系统
python main.py query "你的问题"

# 批量处理目录中的PDF
python main.py batch_process /path/to/pdf/directory

# 高级批量处理（支持并发）
python scripts/batch_processor.py /path/to/pdf/directory --max-workers 8

# 验证处理数据
python scripts/data_validator.py --output validation_report.txt
```

### 设置和配置
```bash
# 初始化项目
python setup.py install

# 创建配置文件（复制模板并编辑）
cp config/settings.json.template config/settings.json
# 然后编辑配置你的API密钥和设置
```

## 架构概览

### 核心处理流水线
系统遵循以下架构流程：
```
[PDF输入] → [文档解析器] → [段落合并器] → [内容提取器] → [内容存储]
↓
[OpenAI API摘要器] → [摘要+内容链接] → [Milvus向量索引]
↓
[查询处理器] → [摘要检索] → [内容获取器] → [多步迭代推理] → [最终答案]
```

### 关键组件

#### 1. 文档处理 (`src/core/`)
- **DocumentParser**: 处理PDF解析，支持多OCR引擎（PaddleOCR、Tesseract）
- **ContentExtractor**: 基于语义边界进行智能内容分块
- **ParagraphMerger**: 使用连续性分析检测并合并跨页段落
- **Summarizer**: 使用OpenAI兼容API生成文本和多模态摘要
- **Vectorizer**: 为向量搜索创建嵌入

#### 2. 存储系统 (`src/storage/`)
- **ContentStorage**: 管理文本、图像和表格内容，包含丰富元数据
- **VectorStorage**: 处理Milvus向量数据库操作

#### 3. 检索系统 (`src/retrieval/`)
- **SearchEngine**: 向量相似度搜索，带查询预处理
- **ContentFetcher**: 通过内容链接获取完整内容，支持重试机制

#### 4. Agent系统 (`src/agent/`)
- **IterationController**: 管理多步推理循环
- **ReasoningEngine**: 执行多模态推理
- **AnswerGenerator**: 格式化最终答案并添加来源引用

### 多供应商API支持
系统通过OpenAI兼容API支持多个AI供应商：
- OpenAI (GPT-4, GPT-4V, embeddings)
- Qwen (阿里云)
- Anthropic (Claude)
- 自定义端点

## 配置管理

### 主配置文件
位置：`config/settings.json`

关键部分：
- `api_config`: 不同供应商的API密钥和端点
- `milvus_config`: 向量数据库连接设置
- `model_config`: 模型选择和生成参数
- `processing_config`: OCR引擎、块大小、迭代限制
- `continuity_factors`: 段落合并决策的权重
- `termination_conditions`: 停止迭代推理的标准

### 数据组织结构
```
data/
├── raw_pdfs/              # 原始PDF文件
├── extracted_content/     # 处理后的内容
│   ├── images/           # 提取的图像
│   ├── text/             # 提取的文本
│   └── tables/           # 提取的表格
├── content.db            # SQLite内容存储
└── milvus_lite.db        # Milvus Lite向量存储
```

## 开发指南

### 测试策略
- 每个核心模块的单元测试位于`tests/`
- 端到端工作流的集成测试
- 使用`tests/quick_test.py`进行快速开发测试

### OCR引擎处理
系统优雅处理缺失的OCR依赖：
- PaddleOCR: 针对中文优化
- Tesseract: 多语言支持
- EasyOCR: 备选方案
- 引擎间自动回退

### 内容质量保证
- OCR置信度评分
- 使用哈希进行内容去重
- 提取表格和图像的质量评估
- 所有内容的元数据跟踪（来源、页面、提取方法、质量评分）

### 迭代推理
系统使用复杂的终止条件：
- 答案完整性阈值
- 置信度评分
- 最大迭代次数限制
- 信息增益评估
- 查询特异性分析

## 常见开发模式

### 添加新OCR引擎
1. 在`DocumentParser._validate_ocr_engines()`中添加可用性检查
2. 按照`_paddle_ocr()`模式实现OCR方法
3. 更新配置架构

### 扩展AI供应商
1. 在`api_config.py`中添加供应商配置
2. 更新`APIConfig`中的回退链
3. 测试与OpenAI响应格式的兼容性

### 内容类型扩展
1. 为新内容类型扩展`ContentStorage`方法
2. 更新内容链接生成格式
3. 在`Summarizer`中添加适当的摘要生成

## 依赖和环境

### Python要求
- Python 3.8+
- PyMuPDF用于PDF处理
- PaddleOCR/Tesseract用于OCR（可选，优雅回退）
- pymilvus用于向量存储
- OpenAI兼容API访问
- PIL/Pillow用于图像处理

### 可选依赖
- camelot用于表格提取（不可用时优雅回退）
- EasyOCR作为额外OCR选项

## 调试和监控

### 日志记录
- 使用`src/utils/logger.py`进行全面日志记录
- 可配置的日志级别
- 详细的处理指标

### 数据验证
- 运行`python scripts/data_validator.py`检查数据完整性
- 验证内容链接、向量索引和元数据一致性
- 生成详细的验证报告

该框架专为可扩展性、健壮性和生产环境中的企业PDF处理工作流而设计。