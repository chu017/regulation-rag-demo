"""
End-to-end test script to verify the complete pipeline works.
Tests: parse → chunk → embed → retrieve → strategy
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import RAW_PDF_DIR, PARSED_DIR, CHUNKS_DIR, FAISS_DIR


def test_pipeline_steps():
    """Test each step of the pipeline."""
    print("=" * 60)
    print("End-to-End Pipeline Test")
    print("=" * 60)
    print()
    
    results = {
        "PDFs available": False,
        "Parsed files": False,
        "Chunks created": False,
        "FAISS index": False,
        "Can retrieve": False,
        "Can analyze": False
    }
    
    # Step 1: Check for PDFs
    print("1. Checking for PDF files...")
    pdfs = list(RAW_PDF_DIR.glob("**/*.pdf"))
    if pdfs:
        print(f"   ✅ Found {len(pdfs)} PDF file(s)")
        for pdf in pdfs[:3]:  # Show first 3
            print(f"      - {pdf.relative_to(RAW_PDF_DIR)}")
        if len(pdfs) > 3:
            print(f"      ... and {len(pdfs) - 3} more")
        results["PDFs available"] = True
    else:
        print("   ❌ No PDF files found")
        print(f"      Add PDFs to: {RAW_PDF_DIR}")
    print()
    
    # Step 2: Check for parsed files
    print("2. Checking for parsed JSON files...")
    parsed_files = list(PARSED_DIR.glob("**/*.json"))
    if parsed_files:
        print(f"   ✅ Found {len(parsed_files)} parsed file(s)")
        results["Parsed files"] = True
    else:
        print("   ⚠️  No parsed files found")
        print("      Run: python scripts/parse_pdf.py")
    print()
    
    # Step 3: Check for chunks
    print("3. Checking for chunk files...")
    chunks_file = CHUNKS_DIR / "chunks.jsonl"
    if chunks_file.exists():
        # Count chunks
        chunk_count = sum(1 for _ in open(chunks_file, 'r', encoding='utf-8'))
        print(f"   ✅ Found chunks file with {chunk_count} chunk(s)")
        results["Chunks created"] = True
    else:
        print("   ⚠️  No chunks file found")
        print("      Run: python scripts/chunk_text.py")
    print()
    
    # Step 4: Check for FAISS index
    print("4. Checking for FAISS index...")
    index_file = FAISS_DIR / "faiss.index"
    metadata_file = FAISS_DIR / "metadata.json"
    if index_file.exists() and metadata_file.exists():
        print("   ✅ FAISS index and metadata found")
        results["FAISS index"] = True
        
        # Try to load and test retrieval
        print("5. Testing retrieval...")
        try:
            from scripts.retrieve import retrieve
            test_results = retrieve("ADU requirements", top_k=3)
            if test_results:
                print(f"   ✅ Retrieval works! Retrieved {len(test_results)} chunks")
                results["Can retrieve"] = True
            else:
                print("   ⚠️  Retrieval returned no results")
        except Exception as e:
            print(f"   ❌ Retrieval failed: {e}")
    else:
        print("   ⚠️  FAISS index not found")
        print("      Run: python scripts/embed_index.py")
    print()
    
    # Step 6: Test strategy analysis (if retrieval works)
    if results["Can retrieve"]:
        print("6. Testing strategy analysis...")
        try:
            from scripts.strategy import analyze_strategies
            from scripts.property_api import get_property_info_from_address
            
            # Test with a sample address
            test_address = "123 Main St, San Jose, CA"
            property_info = get_property_info_from_address(test_address)
            test_results = retrieve("development regulations", top_k=3)
            
            strategies = analyze_strategies(property_info, test_results)
            if strategies:
                print(f"   ✅ Strategy analysis works! Analyzed {len(strategies)} strategies")
                results["Can analyze"] = True
            else:
                print("   ⚠️  Strategy analysis returned no results")
        except Exception as e:
            print(f"   ❌ Strategy analysis failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("6. Skipping strategy test (retrieval not available)")
    print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = all(results.values())
    for step, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {step}")
    
    print()
    if all_passed:
        print("🎉 All tests passed! Your pipeline is ready to use.")
        print()
        print("Next steps:")
        print("  1. Run: streamlit run app/app.py")
        print("  2. Enter a property address in the UI")
    else:
        print("⚠️  Some steps need attention. Follow the suggestions above.")
        print()
        print("Quick fix commands:")
        if not results["Parsed files"]:
            print("  python scripts/parse_pdf.py")
        if not results["Chunks created"]:
            print("  python scripts/chunk_text.py")
        if not results["FAISS index"]:
            print("  python scripts/embed_index.py")
    
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = test_pipeline_steps()
    sys.exit(0 if success else 1)
