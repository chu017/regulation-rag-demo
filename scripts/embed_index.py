"""
Generate embeddings using Gemini Embedding API and build FAISS index.
Store: faiss.index and metadata.json mapping chunk_id to source info.
"""
import json
import os
import faiss
import numpy as np
from pathlib import Path
import sys
import requests

sys.path.append(str(Path(__file__).parent.parent))
from config import CHUNKS_DIR, FAISS_DIR, EMBEDDING_MODEL


def load_api_key():
    """Load Gemini API key from environment."""
    from dotenv import load_dotenv
    
    # Load .env from project root (parent directory)
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment. Please set it in .env file")
    
    return api_key


def get_embedding(text, model=EMBEDDING_MODEL, api_key=None):
    """Get embedding for text using Gemini API REST endpoint."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    payload = {
        "content": {
            "parts": [{
                "text": text
            }]
        },
        "taskType": "RETRIEVAL_DOCUMENT"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    result = response.json()
    return result["embedding"]["values"]


def build_index():
    """Build FAISS index from chunks."""
    chunks_file = CHUNKS_DIR / "chunks.jsonl"
    
    if not chunks_file.exists():
        raise FileNotFoundError(f"Chunks file not found: {chunks_file}. Run chunk_text.py first.")
    
    # Load API key
    api_key = load_api_key()
    
    # Load chunks
    chunks = []
    with open(chunks_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
    
    print(f"Loading {len(chunks)} chunks...")
    
    # Generate embeddings
    embeddings = []
    metadata = []
    
    for i, chunk in enumerate(chunks):
        if (i + 1) % 10 == 0:
            print(f"  Processing chunk {i+1}/{len(chunks)}...")
        
        try:
            embedding = get_embedding(chunk["text"], api_key=api_key)
            embeddings.append(embedding)
            
            # Store metadata
            metadata.append({
                "chunk_id": chunk["chunk_id"],
                "city": chunk.get("city"),
                "zoning": chunk.get("zoning"),
                "page_start": chunk.get("page_start"),
                "page_end": chunk.get("page_end"),
                "line_start": chunk.get("line_start"),
                "line_end": chunk.get("line_end"),
                "regulation": chunk.get("regulation"),
                "text": chunk["text"]  # Store text for retrieval
            })
        except Exception as e:
            print(f"Error embedding chunk {chunk['chunk_id']}: {e}")
            continue
    
    if not embeddings:
        raise ValueError("No embeddings generated. Check API key and chunks file.")
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings).astype('float32')
    dimension = embeddings_array.shape[1]
    
    print(f"Embedding dimension: {dimension}")
    print(f"Total embeddings: {len(embeddings_array)}")
    
    # Build FAISS index (L2 distance)
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)
    
    # Save index
    index_path = FAISS_DIR / "faiss.index"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_path))
    print(f"Saved FAISS index to: {index_path}")
    
    # Save metadata
    metadata_path = FAISS_DIR / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"Saved metadata to: {metadata_path}")
    
    print(f"\nIndex built successfully!")
    print(f"  - Index size: {index.ntotal}")
    print(f"  - Dimension: {dimension}")


if __name__ == "__main__":
    build_index()
