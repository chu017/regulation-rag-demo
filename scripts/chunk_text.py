"""
Chunk parsed text into retrieval-sized chunks (600-800 tokens).
Each chunk includes: city, zoning (if available), page_start, page_end, line numbers.
"""
import json
import tiktoken
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import PARSED_DIR, CHUNKS_DIR, CHUNK_SIZE, CHUNK_OVERLAP


def count_tokens(text, encoding_name="cl100k_base"):
    """Count tokens in text using tiktoken."""
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text))


def chunk_text(pages_data, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    """
    Split pages into chunks with metadata.
    
    Args:
        pages_data: List of page objects from parse_pdf
        chunk_size: Target tokens per chunk
        chunk_overlap: Overlap tokens between chunks
    
    Returns:
        List of chunk objects with metadata
    """
    chunks = []
    current_chunk = []
    current_tokens = 0
    chunk_id = 0
    
    # Extract metadata from first page
    city = pages_data[0].get("city") if pages_data else None
    regulation = pages_data[0].get("regulation") if pages_data else None
    
    for page_idx, page_data in enumerate(pages_data):
        page_num = page_data["page"]
        text = page_data["text"]
        text_tokens = count_tokens(text)
        
        # If single page exceeds chunk size, split it
        if text_tokens > chunk_size:
            # Split page text by sentences/paragraphs
            paragraphs = text.split("\n\n")
            for para in paragraphs:
                para_tokens = count_tokens(para)
                
                if current_tokens + para_tokens > chunk_size and current_chunk:
                    # Save current chunk
                    chunk_text = "\n\n".join([p["text"] for p in current_chunk])
                    chunks.append({
                        "chunk_id": f"{regulation}_{chunk_id}" if regulation else f"chunk_{chunk_id}",
                        "text": chunk_text,
                        "city": city,
                        "zoning": None,  # Will be extracted later if available
                        "page_start": current_chunk[0]["page"],
                        "page_end": current_chunk[-1]["page"],
                        "line_start": 1,  # Approximate
                        "line_end": len(chunk_text.split("\n")),
                        "regulation": regulation
                    })
                    chunk_id += 1
                    
                    # Start new chunk with overlap
                    if chunk_overlap > 0 and current_chunk:
                        # Keep last few paragraphs for overlap
                        overlap_text = "\n\n".join([p["text"] for p in current_chunk[-2:]])
                        current_chunk = [{"text": overlap_text, "page": current_chunk[-1]["page"]}]
                        current_tokens = count_tokens(overlap_text)
                    else:
                        current_chunk = []
                        current_tokens = 0
                
                current_chunk.append({"text": para, "page": page_num})
                current_tokens += para_tokens
        
        else:
            # Check if adding this page would exceed chunk size
            if current_tokens + text_tokens > chunk_size and current_chunk:
                # Save current chunk
                chunk_text = "\n\n".join([p["text"] for p in current_chunk])
                chunks.append({
                    "chunk_id": f"{regulation}_{chunk_id}" if regulation else f"chunk_{chunk_id}",
                    "text": chunk_text,
                    "city": city,
                    "zoning": None,
                    "page_start": current_chunk[0]["page"],
                    "page_end": current_chunk[-1]["page"],
                    "line_start": 1,
                    "line_end": len(chunk_text.split("\n")),
                    "regulation": regulation
                })
                chunk_id += 1
                
                # Start new chunk with overlap
                if chunk_overlap > 0 and current_chunk:
                    overlap_text = "\n\n".join([p["text"] for p in current_chunk[-1:]])
                    current_chunk = [{"text": overlap_text, "page": current_chunk[-1]["page"]}]
                    current_tokens = count_tokens(overlap_text)
                else:
                    current_chunk = []
                    current_tokens = 0
            
            current_chunk.append({"text": text, "page": page_num})
            current_tokens += text_tokens
    
    # Save final chunk
    if current_chunk:
        chunk_text = "\n\n".join([p["text"] for p in current_chunk])
        chunks.append({
            "chunk_id": f"{regulation}_{chunk_id}" if regulation else f"chunk_{chunk_id}",
            "text": chunk_text,
            "city": city,
            "zoning": None,
            "page_start": current_chunk[0]["page"],
            "page_end": current_chunk[-1]["page"],
            "line_start": 1,
            "line_end": len(chunk_text.split("\n")),
            "regulation": regulation
        })
    
    return chunks


def extract_zoning_from_text(text):
    """Extract zoning information from text if available."""
    # Simple keyword-based extraction (can be enhanced)
    zoning_keywords = ["R-1", "R-2", "R-3", "R-4", "C-1", "C-2", "M-1", "M-2", 
                      "residential", "commercial", "mixed-use", "zoning"]
    
    text_lower = text.lower()
    for keyword in zoning_keywords:
        if keyword.lower() in text_lower:
            # Try to extract full zoning code
            idx = text_lower.find(keyword.lower())
            snippet = text[max(0, idx-20):min(len(text), idx+50)]
            # This is a simple extraction - can be improved
            return keyword.upper()
    
    return None


def process_all_parsed_files():
    """Process all parsed JSON files and create chunks."""
    parsed_dir = Path(PARSED_DIR)
    
    if not parsed_dir.exists():
        print(f"Parsed directory not found: {parsed_dir}")
        print("Please run parse_pdf.py first")
        return
    
    # Find all JSON files
    json_files = list(parsed_dir.glob("**/*.json"))
    
    if not json_files:
        print(f"No parsed JSON files found in {parsed_dir}")
        return
    
    all_chunks = []
    
    for json_file in json_files:
        print(f"Processing: {json_file}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                pages_data = json.load(f)
            
            chunks = chunk_text(pages_data)
            
            # Try to extract zoning from chunks
            for chunk in chunks:
                zoning = extract_zoning_from_text(chunk["text"])
                if zoning:
                    chunk["zoning"] = zoning
            
            all_chunks.extend(chunks)
            print(f"  Created {len(chunks)} chunks")
            
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
            continue
    
    # Save all chunks to JSONL file
    chunks_file = CHUNKS_DIR / "chunks.jsonl"
    chunks_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(chunks_file, 'w', encoding='utf-8') as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    
    print(f"\nTotal chunks created: {len(all_chunks)}")
    print(f"Saved to: {chunks_file}")


if __name__ == "__main__":
    process_all_parsed_files()
