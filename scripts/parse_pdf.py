"""
Parse PDF regulation documents into page-aware text with table extraction.
Output: JSON file per PDF with page, text, and table markdown.
"""
import json
import pdfplumber
import camelot
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config import RAW_PDF_DIR, PARSED_DIR


def extract_tables_markdown(pdf_path, page_num):
    """Extract tables from a page and convert to markdown format."""
    try:
        tables = camelot.read_pdf(str(pdf_path), pages=str(page_num), flavor='lattice')
        if len(tables) == 0:
            return None
        
        markdown_tables = []
        for table in tables:
            df = table.df
            # Convert DataFrame to markdown
            markdown = df.to_markdown(index=False)
            markdown_tables.append(markdown)
        
        return "\n\n".join(markdown_tables) if markdown_tables else None
    except Exception as e:
        print(f"Warning: Could not extract tables from page {page_num}: {e}")
        return None


def parse_pdf(pdf_path, city=None, regulation=None):
    """
    Parse a PDF file into structured text with page numbers.
    
    Args:
        pdf_path: Path to PDF file
        city: City name (extracted from directory structure)
        regulation: Regulation name (extracted from filename)
    
    Returns:
        List of page objects with text and tables
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    pages_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            # Extract text
            text = page.extract_text()
            if not text or not text.strip():
                continue
            
            # Extract tables as markdown
            table_markdown = extract_tables_markdown(pdf_path, page_num)
            
            # Combine text and tables
            full_text = text
            if table_markdown:
                full_text += f"\n\n## Tables on Page {page_num}\n\n{table_markdown}"
            
            pages_data.append({
                "page": page_num,
                "text": full_text.strip(),
                "city": city,
                "regulation": regulation
            })
    
    return pages_data


def save_parsed_data(pages_data, output_path):
    """Save parsed pages to JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(pages_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(pages_data)} pages to {output_path}")


def main():
    """Parse all PDFs in raw directory structure."""
    raw_dir = Path(RAW_PDF_DIR)
    
    if not raw_dir.exists():
        print(f"Raw PDF directory not found: {raw_dir}")
        print("Please create directory structure: data/raw/{city}/{regulation}.pdf")
        return
    
    # Find all PDFs in city/regulation structure
    pdf_files = list(raw_dir.glob("**/*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {raw_dir}")
        print("Expected structure: data/raw/{city}/{regulation}.pdf")
        return
    
    for pdf_path in pdf_files:
        # Extract city and regulation from path
        relative_path = pdf_path.relative_to(raw_dir)
        parts = relative_path.parts
        
        if len(parts) >= 2:
            city = parts[0]
            regulation = pdf_path.stem
        else:
            city = None
            regulation = pdf_path.stem
        
        print(f"Parsing: {pdf_path} (city: {city}, regulation: {regulation})")
        
        try:
            pages_data = parse_pdf(pdf_path, city=city, regulation=regulation)
            
            # Save to parsed directory
            if city:
                output_path = PARSED_DIR / city / f"{regulation}.json"
            else:
                output_path = PARSED_DIR / f"{regulation}.json"
            
            save_parsed_data(pages_data, output_path)
            
        except Exception as e:
            print(f"Error parsing {pdf_path}: {e}")
            continue


if __name__ == "__main__":
    main()
