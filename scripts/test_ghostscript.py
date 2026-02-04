"""
Quick test script to verify Ghostscript is installed and accessible.
Run this BEFORE parse_pdf.py to ensure table extraction will work.
"""
import subprocess
import sys
import platform


def test_ghostscript():
    """Test if Ghostscript is installed and accessible."""
    print("Testing Ghostscript installation...")
    print("=" * 50)
    
    # Determine the correct command based on OS
    if platform.system() == "Windows":
        commands = ['gswin64c', 'gswin32c', 'gs']
    else:
        commands = ['gs']
    
    found = False
    for cmd in commands:
        try:
            result = subprocess.run(
                [cmd, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✅ Ghostscript found: {cmd}")
                print(f"   Version: {result.stdout.strip()}")
                found = True
                break
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            print(f"⚠️  Command '{cmd}' timed out")
            continue
        except Exception as e:
            continue
    
    if not found:
        print("❌ Ghostscript NOT FOUND")
        print("\nPlease install Ghostscript:")
        print("  Windows: Download from https://www.ghostscript.com/download/gsdnld.html")
        print("  macOS:   brew install ghostscript")
        print("  Linux:   sudo apt-get install ghostscript")
        print("\nSee GHOSTSCRIPT_INSTALL.md for detailed instructions")
        return False
    
    # Test camelot import
    print("\nTesting camelot-py...")
    try:
        import camelot
        print("✅ camelot-py is installed")
        
        # Try to verify camelot can find ghostscript
        # Note: camelot doesn't expose a direct way to test this,
        # but if it's imported successfully, it should work
        print("✅ camelot-py should be able to use Ghostscript")
        return True
    except ImportError:
        print("❌ camelot-py is not installed")
        print("   Run: pip install camelot-py[cv]")
        return False


def test_table_extraction():
    """Test if table extraction would work (requires a test PDF)."""
    print("\n" + "=" * 50)
    print("Optional: Test table extraction")
    print("=" * 50)
    print("To fully test table extraction, you need a PDF with tables.")
    print("The parse_pdf.py script will show warnings if extraction fails.")


if __name__ == "__main__":
    success = test_ghostscript()
    test_table_extraction()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Ready to run parse_pdf.py!")
    else:
        print("❌ Please install Ghostscript before running parse_pdf.py")
        sys.exit(1)
