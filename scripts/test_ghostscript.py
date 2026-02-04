"""
Quick test script to verify Ghostscript is installed and accessible.
Run this BEFORE parse_pdf.py to ensure table extraction will work.
"""
import subprocess
import sys
import platform
from pathlib import Path

# Use ASCII-safe characters for Windows compatibility
CHECK = "[OK]"
CROSS = "[X]"
WARN = "[!]"


def test_ghostscript():
    """Test if Ghostscript is installed and accessible."""
    print("Testing Ghostscript installation...")
    print("=" * 50)
    
    found = False
    
    # Determine the correct command based on OS
    if platform.system() == "Windows":
        # Try common installation paths first
        # Note: Some installations have nested bin\bin directories
        common_paths = [
            r"C:\Program Files\gs\gs10.06.0\bin\bin\gswin64c.exe",  # Nested bin structure
            r"C:\Program Files\gs\gs10.06.0\bin\gswin64c.exe",     # Standard structure
            r"C:\Program Files\gs\gs10.05.0\bin\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.05.0\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.04.0\bin\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.04.0\bin\gswin64c.exe",
            r"C:\Program Files (x86)\gs\gs10.06.0\bin\bin\gswin32c.exe",
            r"C:\Program Files (x86)\gs\gs10.06.0\bin\gswin32c.exe",
        ]
        
        # Check common paths
        for gs_path in common_paths:
            if Path(gs_path).exists():
                try:
                    result = subprocess.run(
                        [gs_path, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        print(f"{CHECK} Ghostscript found at: {gs_path}")
                        print(f"   Version: {result.stdout.strip()}")
                        found = True
                        break
                except Exception:
                    continue
        
        # Also try commands in PATH
        if not found:
            commands = ['gswin64c', 'gswin32c', 'gs']
            for cmd in commands:
                try:
                    result = subprocess.run(
                        [cmd, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        print(f"{CHECK} Ghostscript found in PATH: {cmd}")
                        print(f"   Version: {result.stdout.strip()}")
                        found = True
                        break
                except FileNotFoundError:
                    continue
                except subprocess.TimeoutExpired:
                    print(f"{WARN} Command '{cmd}' timed out")
                    continue
                except Exception:
                    continue
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
                    print(f"{CHECK} Ghostscript found: {cmd}")
                    print(f"   Version: {result.stdout.strip()}")
                    found = True
                    break
            except FileNotFoundError:
                continue
            except subprocess.TimeoutExpired:
                print(f"{WARN} Command '{cmd}' timed out")
                continue
            except Exception:
                continue
    
    if not found:
        print(f"{CROSS} Ghostscript NOT FOUND")
        print("\nPossible issues:")
        print("  1. Ghostscript may not be fully installed")
        print("  2. Ghostscript may not be in your system PATH")
        print("  3. Installation may be incomplete")
        print("\nSolutions:")
        print("  - Reinstall Ghostscript from: https://www.ghostscript.com/download/gsdnld.html")
        print("  - During installation, ensure 'Add Ghostscript to PATH' is checked")
        print("  - Or manually add Ghostscript bin directory to your system PATH")
        print("\nIf you know the installation path, you can add it to PATH:")
        print("  Example: C:\\Program Files\\gs\\gs10.06.0\\bin")
        print("\nSee GHOSTSCRIPT_INSTALL.md for detailed instructions")
        return False
    
    # Test camelot import
    print("\nTesting camelot-py...")
    try:
        import camelot
        print(f"{CHECK} camelot-py is installed")
        
        # Try to verify camelot can find ghostscript
        # Note: camelot doesn't expose a direct way to test this,
        # but if it's imported successfully, it should work
        print(f"{CHECK} camelot-py should be able to use Ghostscript")
        return True
    except ImportError:
        print(f"{CROSS} camelot-py is not installed")
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
        print(f"{CHECK} Ready to run parse_pdf.py!")
    else:
        print(f"{CROSS} Please install Ghostscript before running parse_pdf.py")
        sys.exit(1)
