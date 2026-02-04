# How to Install Ghostscript

Ghostscript is required for table extraction from PDFs using `camelot-py`. Follow the instructions for your operating system below.

## Why Ghostscript?

The `camelot-py` library (used in `scripts/parse_pdf.py`) requires Ghostscript to extract tables from PDF files. Without it, you'll get errors when parsing PDFs with tables.

## Installation by Operating System

### Windows

#### Option 1: Official Installer (Recommended)

1. **Download Ghostscript**
   - Go to: https://www.ghostscript.com/download/gsdnld.html
   - Download the latest version (e.g., `gs10xx.x64.exe` for 64-bit Windows)
   - Choose the **AGPL release** (free, open-source)

2. **Run the Installer**
   - Double-click the downloaded `.exe` file
   - Follow the installation wizard
   - **Important**: During installation, check "Add Ghostscript to PATH" if available
   - Default installation path: `C:\Program Files\gs\gs10.x.x\bin`

3. **Verify Installation**
   Open PowerShell or Command Prompt and run:
   ```powershell
   gswin64c --version
   ```
   You should see version information. If you get "command not found", you may need to add Ghostscript to your PATH manually.

#### Option 2: Using Chocolatey (If you have it)

```powershell
choco install ghostscript
```

#### Option 3: Manual PATH Configuration

If Ghostscript is installed but not found:

1. Find the installation directory (usually `C:\Program Files\gs\gs10.x.x\bin`)
2. Add it to your system PATH:
   - Right-click "This PC" → Properties → Advanced System Settings
   - Click "Environment Variables"
   - Under "System Variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\Program Files\gs\gs10.x.x\bin` (replace with your version)
   - Click OK on all dialogs
   - **Restart your terminal/PowerShell** for changes to take effect

### macOS

#### Option 1: Using Homebrew (Recommended)

```bash
brew install ghostscript
```

#### Option 2: Using MacPorts

```bash
sudo port install ghostscript
```

#### Verify Installation

```bash
gs --version
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install ghostscript
```

For table extraction, you may also need:

```bash
sudo apt-get install ghostscript python3-tk
```

#### Verify Installation

```bash
gs --version
```

### Linux (Fedora/RHEL/CentOS)

```bash
sudo dnf install ghostscript
# or for older systems:
sudo yum install ghostscript
```

### Linux (Arch)

```bash
sudo pacman -S ghostscript
```

## Verify Installation in Python

After installing Ghostscript, verify it works with Python:

```python
import subprocess
import sys

try:
    # Try to run ghostscript
    result = subprocess.run(['gs', '--version'], 
                          capture_output=True, 
                          text=True)
    if result.returncode == 0:
        print(f"✅ Ghostscript installed: {result.stdout.strip()}")
    else:
        print("❌ Ghostscript not found in PATH")
except FileNotFoundError:
    # On Windows, try gswin64c
    try:
        result = subprocess.run(['gswin64c', '--version'], 
                              capture_output=True, 
                              text=True)
        if result.returncode == 0:
            print(f"✅ Ghostscript installed: {result.stdout.strip()}")
        else:
            print("❌ Ghostscript not found")
    except FileNotFoundError:
        print("❌ Ghostscript not installed or not in PATH")
```

Or test with camelot directly:

```python
import camelot

# This should work without errors if Ghostscript is installed
print("✅ camelot-py can find Ghostscript")
```

## Troubleshooting

### "Ghostscript not found" Error

**Windows:**
- Make sure Ghostscript is installed
- Check if `gswin64c.exe` exists in `C:\Program Files\gs\`
- Add Ghostscript bin directory to PATH (see manual PATH configuration above)
- Restart your terminal/IDE after adding to PATH

**macOS/Linux:**
- Verify installation: `which gs` should show the path
- If not found, reinstall using the package manager
- Make sure you're using the correct package manager for your system

### "Table extraction fails" but Ghostscript is installed

1. **Check camelot-py installation:**
   ```bash
   pip install --upgrade camelot-py[cv]
   ```

2. **Verify Ghostscript version:**
   - Older versions may have issues
   - Update to the latest version if possible

3. **Check PDF format:**
   - Some scanned PDFs (images) won't work
   - Try with a text-based PDF first

### Test Table Extraction

After installation, test with a sample PDF:

```python
import camelot

# Try extracting tables from a PDF
tables = camelot.read_pdf('test.pdf', pages='1')
print(f"Found {len(tables)} tables")
```

## Alternative: Skip Table Extraction

If you don't need table extraction, you can modify `scripts/parse_pdf.py` to skip the table extraction step. However, this will reduce the quality of regulation parsing if your PDFs contain important tables.

## Need Help?

- **Official Ghostscript Docs**: https://www.ghostscript.com/documentation.html
- **camelot-py Docs**: https://camelot-py.readthedocs.io/
- **Common Issues**: Check the troubleshooting section above
