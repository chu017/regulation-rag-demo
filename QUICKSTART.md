# Quick Start Guide

## Prerequisites
- Python 3.8+
- Gemini API key

## Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note for table extraction**: Install Ghostscript:
- Windows: Download from [ghostscript.com](https://www.ghostscript.com/download/gsdnld.html)
- Linux: `sudo apt-get install ghostscript python3-tk`
- macOS: `brew install ghostscript`

### 2. Configure API Key
Create a `.env` file in the project root with your Gemini API key:
```bash
# Create .env file (or edit if it already exists)
# Add this line:
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Add Regulation PDFs
Organize PDFs in this structure:
```
data/raw/
├── San Francisco/
│   └── zoning_code.pdf
├── Oakland/
│   └── development_regulations.pdf
└── ...
```

### 4. Build the Index
Run these scripts in order:
```bash
# Parse PDFs
python scripts/parse_pdf.py

# Chunk text
python scripts/chunk_text.py

# Build FAISS index
python scripts/embed_index.py
```

### 5. Run the Demo
```bash
streamlit run app/app.py
```

Open your browser to `http://localhost:8501` and enter a Bay Area address!

## Troubleshooting

**"No PDF files found"**: Make sure PDFs are in `data/raw/{city}/` structure

**"GEMINI_API_KEY not found"**: Check your `.env` file exists and has the key

**"FAISS index not found"**: Run `python scripts/embed_index.py` first

**Table extraction fails**: Install Ghostscript (see Prerequisites)

**Verify your setup**: Run `python scripts/verify_setup.py` to check everything is configured correctly

## What's Next?

- Integrate real property APIs (replace `scripts/property_api.py`)
- Add more cities and regulations
- Fine-tune chunk size and retrieval parameters in `config.py`
- Enhance zoning extraction logic in `scripts/chunk_text.py`
