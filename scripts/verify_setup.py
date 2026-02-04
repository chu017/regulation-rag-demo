"""
Quick verification script to check if the setup is correct.
Run this to verify your environment is configured properly.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def check_env_file():
    """Check if .env file exists and has API key."""
    env_path = Path(__file__).parent.parent / ".env"
    
    if not env_path.exists():
        print("❌ .env file not found")
        print("   Create a .env file with: GEMINI_API_KEY=your_key_here")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False
    
    if api_key == "your_api_key_here" or len(api_key) < 10:
        print("⚠️  GEMINI_API_KEY appears to be a placeholder")
        print("   Please update .env with your actual API key")
        return False
    
    print("✅ .env file configured correctly")
    return True


def check_dependencies():
    """Check if required packages are installed."""
    required = [
        "pdfplumber",
        "camelot",
        "tiktoken",
        "faiss",
        "google.generativeai",
        "dotenv",
        "streamlit",
        "pandas",
        "requests"
    ]
    
    missing = []
    for package in required:
        try:
            if package == "dotenv":
                __import__("dotenv")
            elif package == "camelot":
                __import__("camelot")
            elif package == "faiss":
                __import__("faiss")
            else:
                __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed")
    return True


def check_directories():
    """Check if required directories exist."""
    from config import RAW_PDF_DIR, PARSED_DIR, CHUNKS_DIR, FAISS_DIR
    
    dirs = {
        "Raw PDFs": RAW_PDF_DIR,
        "Parsed": PARSED_DIR,
        "Chunks": CHUNKS_DIR,
        "FAISS": FAISS_DIR
    }
    
    all_exist = True
    for name, path in dirs.items():
        if path.exists():
            print(f"✅ {name} directory: {path}")
        else:
            print(f"❌ {name} directory missing: {path}")
            all_exist = False
    
    return all_exist


def check_data_files():
    """Check if data files exist."""
    from config import RAW_PDF_DIR, CHUNKS_DIR, FAISS_DIR
    
    # Check for PDFs
    pdfs = list(RAW_PDF_DIR.glob("**/*.pdf"))
    if pdfs:
        print(f"✅ Found {len(pdfs)} PDF file(s) in {RAW_PDF_DIR}")
    else:
        print(f"⚠️  No PDF files found in {RAW_PDF_DIR}")
        print("   Add PDFs to: data/raw/{city}/{regulation}.pdf")
    
    # Check for chunks
    chunks_file = CHUNKS_DIR / "chunks.jsonl"
    if chunks_file.exists():
        print(f"✅ Chunks file exists: {chunks_file}")
    else:
        print(f"⚠️  Chunks file not found: {chunks_file}")
        print("   Run: python scripts/chunk_text.py")
    
    # Check for FAISS index
    index_file = FAISS_DIR / "faiss.index"
    if index_file.exists():
        print(f"✅ FAISS index exists: {index_file}")
    else:
        print(f"⚠️  FAISS index not found: {index_file}")
        print("   Run: python scripts/embed_index.py")
    
    return True


def check_ghostscript():
    """Check if Ghostscript is installed."""
    import subprocess
    import platform
    
    if platform.system() == "Windows":
        commands = ['gswin64c', 'gswin32c', 'gs']
    else:
        commands = ['gs']
    
    for cmd in commands:
        try:
            result = subprocess.run(
                [cmd, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✅ Ghostscript found: {result.stdout.strip()}")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    print("⚠️  Ghostscript not found (required for table extraction)")
    print("   See GHOSTSCRIPT_INSTALL.md for installation instructions")
    return False


def main():
    print("=" * 50)
    print("Regulation RAG MVP - Setup Verification")
    print("=" * 50)
    print()
    
    results = []
    
    print("1. Checking environment configuration...")
    results.append(check_env_file())
    print()
    
    print("2. Checking dependencies...")
    results.append(check_dependencies())
    print()
    
    print("3. Checking Ghostscript...")
    check_ghostscript()  # Warning only, not blocking
    print()
    
    print("4. Checking directory structure...")
    results.append(check_directories())
    print()
    
    print("5. Checking data files...")
    check_data_files()
    print()
    
    print("=" * 50)
    if all(results):
        print("✅ Setup looks good! You're ready to go.")
        print()
        print("Next steps:")
        if not list(Path(__file__).parent.parent.glob("data/raw/**/*.pdf")):
            print("  1. Add PDF files to data/raw/{city}/")
        print("  2. Run: python scripts/parse_pdf.py")
        print("  3. Run: python scripts/chunk_text.py")
        print("  4. Run: python scripts/embed_index.py")
        print("  5. Run: streamlit run app/app.py")
    else:
        print("⚠️  Some issues found. Please fix them before proceeding.")
    print("=" * 50)


if __name__ == "__main__":
    main()
