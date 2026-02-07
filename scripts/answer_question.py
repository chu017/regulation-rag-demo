"""
Generate an answer to a user question using property context and retrieved regulation chunks.
Returns the answer plus evidence traceback (source file, page, line) from the raw PDF sources.
"""
import os
import requests
from pathlib import Path
from typing import Dict, List, Any

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import GENERATION_MODEL


def load_api_key():
    """Load Gemini API key from environment."""
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment")
    return api_key


def build_evidence_list(retrieved_chunks: List[Dict]) -> List[Dict[str, Any]]:
    """
    Build evidence list from retrieved chunks for traceback to original PDF source.
    Each evidence item has: source_file (regulation doc name), page, line_start, line_end, text excerpt.
    """
    evidence = []
    for chunk in retrieved_chunks:
        # regulation is the source document name (PDF stem); can display as filename
        source_file = chunk.get("regulation") or "Unknown"
        if source_file != "Unknown" and not source_file.lower().endswith(".pdf"):
            source_file = f"{source_file}.pdf"
        evidence.append({
            "source_file": source_file,
            "page_start": chunk.get("page_start"),
            "page_end": chunk.get("page_end"),
            "line_start": chunk.get("line_start"),
            "line_end": chunk.get("line_end"),
            "text": chunk.get("text", "")[:500],  # excerpt for display
            "chunk_id": chunk.get("chunk_id"),
        })
    return evidence


def answer_question(
    property_info: Dict,
    user_question: str,
    retrieved_chunks: List[Dict],
) -> Dict[str, Any]:
    """
    Generate an answer to the user's question using property context and retrieved regulations.
    Uses only the provided chunks; cites source file, page, and line for every claim.

    Args:
        property_info: Dict with address, city, zoning, lot_size_sqft, etc.
        user_question: The user's question (e.g. "Can I build an ADU?")
        retrieved_chunks: List of chunks from retrieve()

    Returns:
        Dict with:
          - answer: str (generated answer)
          - evidence: list of { source_file, page_start, page_end, line_start, line_end, text }
    """
    if not retrieved_chunks:
        return {
            "answer": "No relevant regulation excerpts were found for your property and question. Please ensure the address is in a supported area and that the regulation index has been built.",
            "evidence": [],
        }

    # Build evidence list for traceback (file, page, line)
    evidence = build_evidence_list(retrieved_chunks)

    # Format regulation excerpts with clear source citations for the LLM
    regulation_text = ""
    for i, chunk in enumerate(retrieved_chunks):
        regulation_text += f"\n\n--- Source {i+1} ---\n"
        regulation_text += f"Source file: {chunk.get('regulation', 'Unknown')}.pdf\n"
        regulation_text += f"Page: {chunk.get('page_start')}-{chunk.get('page_end')}\n"
        regulation_text += f"Lines: {chunk.get('line_start')}-{chunk.get('line_end')}\n"
        regulation_text += f"Text:\n{chunk.get('text', '')}\n"

    system_prompt = """You are a regulation Q&A assistant. Answer the user's question using ONLY the provided property information and regulation excerpts.

RULES:
1. Use ONLY the provided regulation text. Do not use external knowledge.
2. For every claim or requirement you state, cite the source: file name, page number, and line range (e.g. "Source: SF_Zoning.pdf, Page 10, Lines 1-15").
3. If the answer is not in the provided text, say "NOT FOUND in the provided regulations" for that part.
4. Do not give legal advice; only summarize what the regulations state.
5. Be specific: mention exact numbers (lot size, setbacks, etc.) and cite where they come from."""

    user_prompt = f"""Property information:
- Address: {property_info.get('address', 'Unknown')}
- City: {property_info.get('city', 'Unknown')}
- Zoning: {property_info.get('zoning', 'Unknown')}
- Lot size: {property_info.get('lot_size_sqft')} sqft
- Existing units: {property_info.get('existing_units')}

User question: {user_question}

Relevant regulation excerpts (with source file, page, and line info):
{regulation_text}

Provide a clear answer that:
1. Directly addresses the user's question.
2. Cites source file name, page, and line numbers for every factual claim.
3. Notes when information is missing from the provided excerpts."""

    api_key = load_api_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GENERATION_MODEL}:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    payload = {
        "contents": [{
            "parts": [{"text": system_prompt + "\n\n" + user_prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        if "candidates" in result and result["candidates"]:
            parts = result["candidates"][0].get("content", {}).get("parts", [])
            if parts and "text" in parts[0]:
                answer = parts[0]["text"]
            else:
                answer = "Error: No text in model response."
        else:
            answer = "Error: No response from model."
    except Exception as e:
        answer = f"Error generating answer: {e}"

    return {"answer": answer, "evidence": evidence}
