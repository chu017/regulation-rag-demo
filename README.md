# Real Estate Regulation AI RAG MVP

A demo-grade RAG (Retrieval-Augmented Generation) system for analyzing real estate development regulations in the Bay Area. This MVP can take a property address, retrieve relevant development regulations, and output feasible strategies (e.g., ADU, SB9) with source citations.

## Project Overview

This system processes local regulation PDFs, chunks them into searchable segments, embeds them using Gemini, and stores them in a FAISS index. When given a property address, it retrieves relevant regulations and uses Gemini to explain development strategy feasibility.

## Features

- **PDF Parsing**: Extracts text and tables from regulation PDFs with page-level tracking
- **Smart Chunking**: Splits regulations into 600-800 token chunks with metadata (city, zoning, page, line)
- **Vector Search**: FAISS-based similarity search with city/zoning filtering
- **Strategy Analysis**: Hard-rule checking (SB9/ADU eligibility) + LLM explanations
- **Source Citations**: Page-level citations for all regulatory claims
- **Streamlit Demo**: Interactive UI for property analysis

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: `camelot-py` requires additional system dependencies for table extraction:
- Windows: Install [Ghostscript](https://www.ghostscript.com/download/gsdnld.html)
- Linux: `sudo apt-get install ghostscript python3-tk`
- macOS: `brew install ghostscript`

### 3. Environment Configuration

Create a `.env` file in the project root with your Gemini API key:

```bash
GEMINI_API_KEY=your_api_key_here
```

**Note**: If `.env.example` exists, you can copy it as a template.

### 4. Prepare Regulation Data

Organize your regulation PDFs in the following structure:

```
data/raw/
├── San Francisco/
│   ├── zoning_code.pdf
│   └── building_code.pdf
├── Oakland/
│   └── development_regulations.pdf
└── ...
```

### 5. Build the Index

Run the processing pipeline:

```bash
# Step 1: Parse PDFs
python scripts/parse_pdf.py

# Step 2: Chunk text
python scripts/chunk_text.py

# Step 3: Generate embeddings and build FAISS index
python scripts/embed_index.py
```

## Running the Demo

Start the Streamlit application:

```bash
streamlit run app/app.py
```

Then open your browser to `http://localhost:8501` and enter a Bay Area property address.

## Project Structure

```
regulation-rag-demo/
├── data/
│   ├── raw/              # Input PDFs (organized by city)
│   ├── parsed/           # Parsed JSON files
│   ├── chunks/           # Chunked text (JSONL)
│   └── faiss/            # FAISS index and metadata
├── scripts/
│   ├── parse_pdf.py      # PDF → text extraction
│   ├── chunk_text.py     # Text → chunks
│   ├── embed_index.py    # Chunks → FAISS index
│   ├── retrieve.py       # FAISS similarity search
│   ├── strategy.py       # Strategy analysis (SB9/ADU)
│   └── property_api.py   # Property lookup (placeholder)
├── app/
│   └── app.py            # Streamlit demo UI
├── prompts/
│   └── strategy_prompt.txt  # LLM system prompt
├── config.py             # Configuration constants
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Workflow

1. **Data Preparation**: Place PDFs in `data/raw/{city}/`
2. **Parsing**: Extract text and tables with page numbers
3. **Chunking**: Split into 600-800 token chunks with metadata
4. **Embedding**: Generate Gemini embeddings and build FAISS index
5. **Retrieval**: Query FAISS with property context (city/zoning filters)
6. **Strategy Matching**: Hard rules + LLM explanation
7. **Generation**: Gemini produces final answer with citations
8. **Frontend**: Streamlit displays results

## Known Limitations

- **Demo-grade**: This is an MVP, not production-ready
- **Single-city focus**: Optimized for Bay Area cities
- **Property API**: Uses placeholder data; integrate real assessor APIs for production
- **Zoning extraction**: Simple keyword-based; may miss complex zoning codes
- **Hard rules**: SB9/ADU eligibility rules are simplified; verify with actual regulations
- **Table extraction**: Requires Ghostscript; may not work for all PDF formats

## Configuration

Edit `config.py` to adjust:
- Chunk size (default: 700 tokens)
- Chunk overlap (default: 100 tokens)
- Top-K retrieval (default: 8 chunks)
- Embedding/generation models

## Troubleshooting

**"FAISS index not found"**: Run `python scripts/embed_index.py` first

**"No chunks found"**: Ensure you've run `parse_pdf.py` and `chunk_text.py`

**Table extraction fails**: Install Ghostscript and ensure PDFs are not scanned images

**API errors**: Verify `GEMINI_API_KEY` is set in `.env` file

**Verify setup**: Run `python scripts/verify_setup.py` to check your configuration

## Disclaimer

**This tool is for demonstration purposes only and does not constitute legal, planning, or professional advice.** Always consult with qualified professionals (attorneys, planners, architects) before making development decisions. Regulations change frequently and vary by jurisdiction.

## License

This is a demo project. Use at your own risk.
