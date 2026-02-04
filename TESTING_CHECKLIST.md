# Testing Checklist

This document outlines all available test scripts and what they verify.

## Available Test Scripts

### 1. `scripts/test_ghostscript.py`
**When to run**: Before running `parse_pdf.py`

**What it tests**:
- ✅ Ghostscript is installed
- ✅ Ghostscript is accessible from command line
- ✅ camelot-py can use Ghostscript

**How to run**:
```bash
python scripts/test_ghostscript.py
```

**Expected output**: 
- ✅ Ghostscript found: [version]
- ✅ camelot-py is installed
- ✅ Ready to run parse_pdf.py!

---

### 2. `scripts/verify_setup.py`
**When to run**: After installing dependencies, before starting the pipeline

**What it tests**:
- ✅ `.env` file exists and has valid API key
- ✅ All Python dependencies are installed
- ✅ Ghostscript is installed (warning if not)
- ✅ Directory structure is correct
- ✅ Data files exist (PDFs, chunks, index)

**How to run**:
```bash
python scripts/verify_setup.py
```

**Expected output**: 
- ✅ Setup looks good! You're ready to go.

---

### 3. `scripts/test_end_to_end.py`
**When to run**: After building the complete index (after running all 3 pipeline scripts)

**What it tests**:
- ✅ PDF files are available
- ✅ Parsed JSON files exist
- ✅ Chunks file exists
- ✅ FAISS index exists
- ✅ Retrieval works
- ✅ Strategy analysis works

**How to run**:
```bash
python scripts/test_end_to_end.py
```

**Expected output**: 
- 🎉 All tests passed! Your pipeline is ready to use.

---

## Testing Workflow

### Initial Setup Testing
```bash
# 1. Test Ghostscript (before parsing)
python scripts/test_ghostscript.py

# 2. Verify overall setup
python scripts/verify_setup.py
```

### After Building Index
```bash
# 3. Test complete pipeline
python scripts/test_end_to_end.py
```

### Manual Testing
```bash
# 4. Test the Streamlit app
streamlit run app/app.py
```

---

## What Each Test Covers

| Test Script | Environment | Dependencies | Ghostscript | Data Files | Pipeline |
|------------|-------------|--------------|-------------|------------|----------|
| `test_ghostscript.py` | ❌ | ❌ | ✅ | ❌ | ❌ |
| `verify_setup.py` | ✅ | ✅ | ⚠️ | ✅ | ❌ |
| `test_end_to_end.py` | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Common Issues and Solutions

### Ghostscript Not Found
**Symptom**: `test_ghostscript.py` fails
**Solution**: Install Ghostscript (see `GHOSTSCRIPT_INSTALL.md`)

### API Key Missing
**Symptom**: `verify_setup.py` shows ❌ for environment
**Solution**: Create `.env` file with `GEMINI_API_KEY=your_key`

### Dependencies Missing
**Symptom**: `verify_setup.py` shows missing packages
**Solution**: Run `pip install -r requirements.txt`

### No PDFs Found
**Symptom**: `test_end_to_end.py` shows no PDFs
**Solution**: Add PDFs to `data/raw/{city}/` directory

### FAISS Index Missing
**Symptom**: `test_end_to_end.py` fails at retrieval
**Solution**: Run `python scripts/embed_index.py`

---

## Next Steps After Testing

Once all tests pass:

1. ✅ Run the Streamlit app: `streamlit run app/app.py`
2. ✅ Test with a real address
3. ✅ Verify citations are working
4. ✅ Check strategy explanations are accurate

---

## Continuous Testing

For development, run tests in this order:

1. **Before parsing**: `test_ghostscript.py`
2. **After setup**: `verify_setup.py`
3. **After pipeline**: `test_end_to_end.py`
4. **Manual UI test**: Streamlit app
