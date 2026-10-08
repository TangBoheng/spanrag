# SpanRAG

**Agentic RAG over PDF documents.**

A Python framework for question answering over PDF documents, built on
retrieval-augmented generation with multi-step iterative reasoning. It handles
both scanned and text-based PDFs: content is extracted via OCR, paragraphs split
across page boundaries are automatically merged, summaries and a vector index are
built, and complex questions are answered through an iterative reasoning loop.

## Features

1. **PDF processing** — handles both scanned and text-based PDF files
2. **OCR** — integrates multiple OCR engines (PaddleOCR, Tesseract, EasyOCR) with automatic fallback
3. **Paragraph merging** — detects and merges paragraphs that span page boundaries
4. **Summarization** — generates text and multimodal summaries using LLM APIs
5. **Vector indexing** — builds an efficient retrieval index on top of Milvus
6. **Iterative reasoning** — multi-step reasoning loop that continues until the answer is complete
7. **Multimodal support** — handles text, images, and tables as distinct content types
8. **Batch processing** — concurrent, multi-threaded processing of large PDF collections
9. **Data validation** — tooling to check data quality and consistency

## Architecture

```
[PDF input] → [OCR parser] → [Paragraph merger] → [Content extractor] → [Content storage]
↓
[LLM summarizer] → [Summary + content links] → [Milvus index]
↓
[Query processor] → [Summary retrieval] → [Content fetch] → [Multi-step reasoning] → [Final answer]
```

## Requirements

- Python 3.8+
- An OpenAI-compatible API endpoint (the project is configured for Alibaba Cloud
  DashScope / Qwen out of the box; OpenAI, Anthropic, and custom endpoints are
  also supported)
- OCR engines are optional — the framework degrades gracefully when they are
  unavailable

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy the template and fill in your own API key:

```bash
cp config/settings.json.template config/settings.json
```

`config/settings.json` is gitignored, so your credentials stay local.

```json
{
    "api_config": {
        "qwen": {
            "api_key": "YOUR_DASHSCOPE_API_KEY",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
        }
    },
    "milvus_config": {
        "collection_name": "rag_documents",
        "uri": "data/milvus_lite.db"
    },
    "model_config": {
        "text_model": "qwen-flash",
        "vision_model": "qwen3-vl-flash",
        "embedding_model": "text-embedding-v4",
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

Keys can also be supplied through the environment (`OPENAI_API_KEY`,
`QWEN_API_KEY`, `ANTHROPIC_API_KEY`) — see `config/settings.py`.

Additional providers can be added under `api_config`; each entry takes an
`api_key` and a `base_url`, so any OpenAI-compatible endpoint works.

## Usage

Commands can be run from the project root as `python main.py <command>`, or after
`pip install -e .` as `spanrag <command>`.

### 1. Process a PDF

```bash
python main.py process_pdf /path/to/your/document.pdf
```

### 2. Ask a question

```bash
python main.py query "your question"
```

### 3. Batch process a directory

```bash
python main.py batch_process /path/to/pdf/directory
```

### 4. Concurrent batch processing

```bash
python scripts/batch_processor.py /path/to/pdf/directory --max-workers 8
```

### 5. Validate processed data

```bash
python scripts/data_validator.py --output validation_report.txt
```

## Project Structure

```
spanrag/
├── config/
│   ├── settings.py               # Configuration loader
│   ├── settings.json.template    # Configuration template (copy to settings.json)
│   ├── api_config.py             # API provider configuration
│   └── milvus_config.py          # Milvus configuration
├── src/
│   ├── core/                     # Core pipeline: parsing, extraction, merging, summarization
│   ├── storage/                  # Content and vector storage
│   ├── retrieval/                # Vector search and content fetching
│   ├── agent/                    # Reasoning engine and iteration control
│   ├── models/                   # Model interfaces (text, vision, embedding)
│   └── utils/                    # Logging, file and filtering helpers
├── data/                         # Generated at runtime (gitignored)
│   ├── raw_pdfs/                 # Source PDF files
│   ├── extracted_content/        # Extracted images, text, tables
│   └── processed/                # Processed output
├── tests/                        # Test suite
├── scripts/                      # Batch processing and validation scripts
├── requirements.txt              # Dependencies
├── setup.py                      # Install script
├── main.py                       # CLI entry point
└── README.md
```

## Development

### Style

- Follow PEP 8
- Use type annotations
- Add unit tests for new modules

### Testing

```bash
# Run the full suite
pytest tests/

# Run a single module verbosely
python -m pytest tests/test_document_parser.py -v
```