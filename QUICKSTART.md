# Quick Start Guide

## Prerequisites
- Python 3.8+
- Gemini API key

## Setup (5 minutes)

### 1. Install Ghostscript (Required BEFORE parsing PDFs)

**⚠️ Important**: Ghostscript must be installed **BEFORE** running `parse_pdf.py`. It's a system-level dependency used automatically by the PDF table extraction.

**Quick install:**
- **Windows**: Download installer from [ghostscript.com](https://www.ghostscript.com/download/gsdnld.html) or use `choco install ghostscript`
- **Linux (Ubuntu/Debian)**: `sudo apt-get install ghostscript python3-tk`
- **macOS**: `brew install ghostscript`

**Verify installation:**
```bash
# Windows
gswin64c --version

# macOS/Linux
gs --version
```

**Detailed instructions**: See [GHOSTSCRIPT_INSTALL.md](GHOSTSCRIPT_INSTALL.md) for step-by-step guide

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the project root with your Gemini API key:
```bash
# Create .env file (or edit if it already exists)
# Add this line:
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Add Regulation PDFs
Organize PDFs in this structure:
```
data/raw/
├── San Francisco/
│   └── zoning_code.pdf
├── Oakland/
│   └── development_regulations.pdf
└── ...
```

### 5. Build the Index
**Optional**: Test Ghostscript first:
```bash
python scripts/test_ghostscript.py
```

Then run these scripts in order:
```bash
# Parse PDFs (uses Ghostscript automatically for table extraction)
python scripts/parse_pdf.py

# Chunk text
python scripts/chunk_text.py

# Build FAISS index
python scripts/embed_index.py
```

### 6. Run the Demo
```bash
streamlit run app/app.py
```

Open your browser to `http://localhost:8501` and enter a Bay Area address!

## Troubleshooting

**"No PDF files found"**: Make sure PDFs are in `data/raw/{city}/` structure

**"GEMINI_API_KEY not found"**: Check your `.env` file exists and has the key

**"FAISS index not found"**: Run `python scripts/embed_index.py` first

**Table extraction fails**: Install Ghostscript (see Step 1 above) and verify with `python scripts/test_ghostscript.py`

**Verify your setup**: Run `python scripts/verify_setup.py` to check everything is configured correctly

**Test Ghostscript before parsing**: Run `python scripts/test_ghostscript.py` to verify Ghostscript is installed correctly

**Test end-to-end pipeline**: After building the index, run `python scripts/test_end_to_end.py` to verify the complete workflow

## What's Next?

- Integrate real property APIs (replace `scripts/property_api.py`)
- Add more cities and regulations
- Fine-tune chunk size and retrieval parameters in `config.py`
- Enhance zoning extraction logic in `scripts/chunk_text.py`
