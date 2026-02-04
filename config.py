"""
Configuration constants for the regulation RAG MVP.
"""
import os
from pathlib import Path

# Model configuration
EMBEDDING_MODEL = "gemini-embedding-001"
GENERATION_MODEL = "gemini-1.5-flash"

# Chunking configuration
CHUNK_SIZE = 700  # Target tokens per chunk (600-800 range)
CHUNK_OVERLAP = 100  # Overlap tokens between chunks

# Retrieval configuration
TOP_K = 8  # Number of chunks to retrieve (5-10 range)

# Data directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_PDF_DIR = DATA_DIR / "raw"
PARSED_DIR = DATA_DIR / "parsed"
CHUNKS_DIR = DATA_DIR / "chunks"
FAISS_DIR = DATA_DIR / "faiss"

# Ensure directories exist
RAW_PDF_DIR.mkdir(parents=True, exist_ok=True)
PARSED_DIR.mkdir(parents=True, exist_ok=True)
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
FAISS_DIR.mkdir(parents=True, exist_ok=True)
