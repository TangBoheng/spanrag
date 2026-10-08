
# 智能Agentic RAG框架

## 项目简介

智能Agentic RAG框架是一个基于检索增强生成（Retrieval-Augmented Generation）技术的智能问答系统。该框架能够处理PDF格式的电子书（包括扫描版和文字版），通过OCR技术提取内容，自动合并跨页段落，生成内容摘要和索引，并支持多步迭代推理来回答复杂问题。

## 核心功能

1. **PDF处理**：支持扫描版和文字版PDF文件处理
2. **OCR识别**：集成多种OCR引擎（PaddleOCR、Tesseract、EasyOCR）
3. **段落合并**：自动检测并合并跨页段落
4. **内容摘要**：使用大语言模型生成文本和多模态内容摘要
5. **向量索引**：基于Milvus构建高效的向量检索系统
6. **智能推理**：支持多步迭代推理直到形成完整答案
7. **多模态支持**：处理文本、图像、表格等多种内容类型
8. **批量处理**：支持多线程并发处理大量PDF文件
9. **数据验证**：提供完整的数据质量检查和验证工具

## 技术架构

```
[PDF输入] → [OCR解析器] → [段落合并器] → [内容截取器] → [内容存储]
↓
[OpenAI API摘要器] → [摘要+链接生成] → [Milvus索引]
↓
[查询处理器] → [摘要检索] → [内容获取] → [多步迭代推理] → [最终答案]
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 处理PDF文件

```bash
python main.py process_pdf /path/to/your/document.pdf
```

### 2. 查询问答

```bash
python main.py query "你的问题"
```

### 3. 批量处理

```bash
python main.py batch_process /path/to/pdf/directory
```

### 4. 高级批量处理（支持并发）

```bash
python scripts/batch_processor.py /path/to/pdf/directory --max-workers 8
```

### 5. 数据验证

```bash
python scripts/data_validator.py --output validation_report.txt
```

## 系统配置

在项目根目录创建`config/settings.json`文件：

```json
{
    "api_config": {
        "openai": {
            "api_key": "",
            "base_url": "https://api.openai.com/v1"
        },
        "qwen": {
            "api_key": "",
            "base_url": "https://dashscope.aliyuncs.com/api/v1"
        },
        "anthropic": {
            "api_key": "",
            "base_url": "https://api.anthropic.com/v1"
        },
        "custom": {
            "api_key": "",
            "base_url": ""
        }
    },
    "milvus_config": {
        "host": "localhost",
        "port": 19530,
        "collection_name": "rag_documents",
        "user": "",
        "password": "",
        "secure": false
    },
    "model_config": {
        "text_model": "gpt-4",
        "vision_model": "gpt-4-vision",
        "embedding_model": "text-embedding-ada-002",
        "temperature": 0.7,
        "max_tokens": 2000
    },
    "processing_config": {
        "chunk_size": 1000,
        "overlap_size": 100,
        "max_iterations": 5,
        "ocr_engines": ["paddleocr", "tesseract", "easyocr"]
    }
}
```

## 项目结构

```
myrag/
├── config/
│   ├── settings.py          # 项目配置文件
│   ├── api_config.py        # API配置
│   └── milvus_config.py     # Milvus配置
├── src/
│   ├── core/                # 核心处理模块
│   ├── storage/             # 存储模块
│   ├── retrieval/           # 检索模块
│   ├── agent/               # 智能代理模块
│   ├── models/              # 模型接口
│   └── utils/               # 工具函数
├── data/
│   ├── raw_pdfs/           # 原始PDF文件
│   ├── extracted_content/  # 提取内容
│   └── processed/          # 处理后数据
├── tests/                  # 测试文件
│   ├── test_document_parser.py
│   ├── test_content_extractor.py
│   ├── test_summarizer.py
│   ├── test_retrieval.py
│   ├── test_agent.py
│   └── test_storage.py
├── scripts/                # 脚本文件
│   ├── batch_processor.py   # 批量处理脚本
│   └── data_validator.py    # 数据验证脚本
├── requirements.txt        # 依赖列表
├── setup.py                # 安装脚本
├── main.py                 # 主程序入口
└── README.md               # 项目说明
```

## 开发指南

### 代码规范

- 遵循PEP 8代码规范
- 使用类型注解
- 编写单元测试

### 测试

```bash
pytest tests/
```

### 运行特定测试

```bash
# 运行文档解析器测试
python -m pytest tests/test_document_parser.py -v

# 运行所有测试
python -m pytest tests/ -v
```



主要更新内容：
1. 更新了配置文件结构，使用新的`api_config`格式
2. 添加了批量处理和数据验证的使用说明
3. 更新了项目结构，包含新增的脚本和测试文件
4. 添加了测试运行说明
5. 补充了新的核心功能描述（批量处理、数据验证）
6. 更新了API配置示例，支持自定义base_url