"""
Retrieve relevant regulation chunks using FAISS similarity search.
Supports filtering by city and zoning.
"""
import json
import os
import google.generativeai as genai
import faiss
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import FAISS_DIR, EMBEDDING_MODEL, TOP_K


def load_api_key():
    """Load Gemini API key from environment."""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment")
    
    return api_key


def get_query_embedding(query_text, model=EMBEDDING_MODEL):
    """Get embedding for query text."""
    result = genai.embed_content(
        model=model,
        content=query_text,
        task_type="RETRIEVAL_QUERY"
    )
    return np.array([result['embedding']]).astype('float32')


def load_index_and_metadata():
    """Load FAISS index and metadata."""
    index_path = FAISS_DIR / "faiss.index"
    metadata_path = FAISS_DIR / "metadata.json"
    
    if not index_path.exists():
        raise FileNotFoundError(f"FAISS index not found: {index_path}. Run embed_index.py first.")
    
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_path}. Run embed_index.py first.")
    
    index = faiss.read_index(str(index_path))
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    return index, metadata


def filter_metadata(metadata, city=None, zoning=None):
    """Filter metadata by city and/or zoning."""
    filtered_indices = []
    
    for idx, item in enumerate(metadata):
        match_city = city is None or item.get("city") == city
        match_zoning = zoning is None or item.get("zoning") == zoning
        
        if match_city and match_zoning:
            filtered_indices.append(idx)
    
    return filtered_indices


def retrieve(query_text, city=None, zoning=None, top_k=TOP_K):
    """
    Retrieve top-K relevant chunks for a query.
    
    Args:
        query_text: Query string
        city: Optional city filter
        zoning: Optional zoning filter
        top_k: Number of results to return
    
    Returns:
        List of chunk dictionaries with similarity scores
    """
    # Initialize API
    api_key = load_api_key()
    genai.configure(api_key=api_key)
    
    # Load index and metadata
    index, metadata = load_index_and_metadata()
    
    # Get query embedding
    query_embedding = get_query_embedding(query_text)
    
    # Filter metadata if filters provided
    if city or zoning:
        filtered_indices = filter_metadata(metadata, city=city, zoning=zoning)
        if not filtered_indices:
            print(f"Warning: No chunks match filters (city={city}, zoning={zoning})")
            return []
        
        # Create filtered index
        filtered_embeddings = []
        filtered_metadata = []
        for idx in filtered_indices:
            # We need to reconstruct embeddings, but we don't have them stored
            # So we'll search all and filter results
            filtered_metadata.append((idx, metadata[idx]))
        
        # Search in full index, then filter results
        k = min(top_k * 3, index.ntotal)  # Get more results to filter
        distances, indices = index.search(query_embedding, k)
        
        # Filter results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if city and metadata[idx].get("city") != city:
                continue
            if zoning and metadata[idx].get("zoning") != zoning:
                continue
            
            results.append({
                "chunk_id": metadata[idx]["chunk_id"],
                "text": metadata[idx]["text"],
                "city": metadata[idx].get("city"),
                "zoning": metadata[idx].get("zoning"),
                "page_start": metadata[idx].get("page_start"),
                "page_end": metadata[idx].get("page_end"),
                "line_start": metadata[idx].get("line_start"),
                "line_end": metadata[idx].get("line_end"),
                "regulation": metadata[idx].get("regulation"),
                "distance": float(dist),
                "similarity": 1.0 / (1.0 + float(dist))  # Convert distance to similarity
            })
            
            if len(results) >= top_k:
                break
        
        return results
    else:
        # No filters - direct search
        k = min(top_k, index.ntotal)
        distances, indices = index.search(query_embedding, k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            results.append({
                "chunk_id": metadata[idx]["chunk_id"],
                "text": metadata[idx]["text"],
                "city": metadata[idx].get("city"),
                "zoning": metadata[idx].get("zoning"),
                "page_start": metadata[idx].get("page_start"),
                "page_end": metadata[idx].get("page_end"),
                "line_start": metadata[idx].get("line_start"),
                "line_end": metadata[idx].get("line_end"),
                "regulation": metadata[idx].get("regulation"),
                "distance": float(dist),
                "similarity": 1.0 / (1.0 + float(dist))
            })
        
        return results


if __name__ == "__main__":
    # Example usage
    query = "What are the requirements for building an ADU?"
    results = retrieve(query, city=None, zoning=None, top_k=5)
    
    print(f"Query: {query}")
    print(f"\nRetrieved {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['chunk_id']} (similarity: {result['similarity']:.3f})")
        print(f"   City: {result['city']}, Zoning: {result['zoning']}")
        print(f"   Pages: {result['page_start']}-{result['page_end']}")
        print(f"   Text preview: {result['text'][:100]}...\n")
