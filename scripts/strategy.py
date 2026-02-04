"""
Strategy matching module: Hard rules for SB9/ADU eligibility + LLM explanation.
"""
import json
import os
import google.generativeai as genai
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import GENERATION_MODEL


def load_api_key():
    """Load Gemini API key from environment."""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment")
    
    return api_key


def check_sb9_eligibility(parcel_attributes):
    """
    Hard rules for SB9 (lot splitting) eligibility.
    
    Args:
        parcel_attributes: Dict with parcel info (lot_size, existing_units, etc.)
    
    Returns:
        Dict with eligibility status and reasons
    """
    lot_size = parcel_attributes.get("lot_size_sqft", 0)
    existing_units = parcel_attributes.get("existing_units", 0)
    zoning = parcel_attributes.get("zoning", "")
    
    eligible = True
    reasons = []
    
    # SB9 requirements (simplified - adjust based on actual regulations)
    if lot_size < 2400:  # Minimum lot size in sqft
        eligible = False
        reasons.append(f"Lot size ({lot_size} sqft) below minimum 2400 sqft")
    
    if existing_units >= 2:
        eligible = False
        reasons.append(f"Property already has {existing_units} units (max 1 allowed for SB9)")
    
    if not zoning or not zoning.startswith("R"):  # Must be residential
        eligible = False
        reasons.append(f"Zoning ({zoning}) not eligible for SB9 (must be residential)")
    
    if eligible:
        reasons.append("Meets basic SB9 eligibility requirements")
    
    return {
        "strategy": "SB9",
        "eligible": eligible,
        "hard_rules": reasons,
        "description": "Senate Bill 9 allows lot splitting for residential development"
    }


def check_adu_eligibility(parcel_attributes):
    """
    Hard rules for ADU (Accessory Dwelling Unit) eligibility.
    
    Args:
        parcel_attributes: Dict with parcel info
    
    Returns:
        Dict with eligibility status and reasons
    """
    lot_size = parcel_attributes.get("lot_size_sqft", 0)
    existing_units = parcel_attributes.get("existing_units", 0)
    zoning = parcel_attributes.get("zoning", "")
    
    eligible = True
    reasons = []
    
    # ADU requirements (simplified)
    if lot_size < 1200:  # Minimum lot size
        eligible = False
        reasons.append(f"Lot size ({lot_size} sqft) below minimum 1200 sqft")
    
    if not zoning or not (zoning.startswith("R") or "residential" in zoning.lower()):
        eligible = False
        reasons.append(f"Zoning ({zoning}) not eligible for ADU")
    
    if eligible:
        reasons.append("Meets basic ADU eligibility requirements")
    
    return {
        "strategy": "ADU",
        "eligible": eligible,
        "hard_rules": reasons,
        "description": "Accessory Dwelling Unit - secondary unit on property"
    }


def generate_strategy_explanation(strategy_result, retrieved_chunks, property_context):
    """
    Use LLM to explain strategy eligibility based on retrieved regulations.
    
    Args:
        strategy_result: Result from check_sb9_eligibility or check_adu_eligibility
        retrieved_chunks: List of retrieved regulation chunks
        property_context: Property information (address, city, zoning, etc.)
    
    Returns:
        Enhanced strategy result with LLM explanation and citations
    """
    api_key = load_api_key()
    genai.configure(api_key=api_key)
    
    # Load prompt template
    prompt_file = Path(__file__).parent.parent / "prompts" / "strategy_prompt.txt"
    if prompt_file.exists():
        with open(prompt_file, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
    else:
        system_prompt = """You are a regulation analysis assistant. Analyze the provided regulation text and explain whether a development strategy is feasible.

Rules:
- Use ONLY the provided regulation text
- Cite page numbers and line numbers when referencing regulations
- If information is missing, say "NOT FOUND"
- Do not make legal claims beyond what the regulations state
- Be specific about requirements and constraints"""
    
    # Format retrieved chunks with citations
    regulation_text = ""
    citations = []
    
    for i, chunk in enumerate(retrieved_chunks):
        citation = {
            "chunk_id": chunk["chunk_id"],
            "page_start": chunk.get("page_start"),
            "page_end": chunk.get("page_end"),
            "regulation": chunk.get("regulation")
        }
        citations.append(citation)
        
        regulation_text += f"\n\n--- Regulation Excerpt {i+1} ---\n"
        regulation_text += f"Source: {chunk.get('regulation', 'Unknown')}\n"
        regulation_text += f"Pages: {chunk.get('page_start')}-{chunk.get('page_end')}\n"
        regulation_text += f"Text:\n{chunk['text']}\n"
    
    # Build prompt
    user_prompt = f"""Property Context:
- Address: {property_context.get('address', 'Unknown')}
- City: {property_context.get('city', 'Unknown')}
- Zoning: {property_context.get('zoning', 'Unknown')}
- Lot Size: {property_context.get('lot_size_sqft', 'Unknown')} sqft
- Existing Units: {property_context.get('existing_units', 'Unknown')}

Strategy: {strategy_result['strategy']}
Hard Rule Eligibility: {'ELIGIBLE' if strategy_result['eligible'] else 'NOT ELIGIBLE'}
Hard Rule Reasons: {', '.join(strategy_result['hard_rules'])}

Relevant Regulations:
{regulation_text}

Please explain:
1. Why this strategy is or is not feasible based on the regulations
2. Specific requirements and constraints from the regulations
3. Cite page numbers for all claims
4. If information is missing, state "NOT FOUND" for that aspect"""
    
    # Generate explanation
    model = genai.GenerativeModel(GENERATION_MODEL)
    
    try:
        response = model.generate_content(system_prompt + "\n\n" + user_prompt)
        explanation = response.text
    except Exception as e:
        explanation = f"Error generating explanation: {e}"
    
    # Enhance strategy result
    strategy_result["explanation"] = explanation
    strategy_result["citations"] = citations
    strategy_result["property_context"] = property_context
    
    return strategy_result


def analyze_strategies(property_context, retrieved_chunks):
    """
    Analyze all development strategies for a property.
    
    Args:
        property_context: Dict with property info (address, city, zoning, lot_size, etc.)
        retrieved_chunks: List of retrieved regulation chunks
    
    Returns:
        List of strategy analysis results
    """
    strategies = []
    
    # Check SB9 eligibility
    sb9_result = check_sb9_eligibility(property_context)
    sb9_result = generate_strategy_explanation(sb9_result, retrieved_chunks, property_context)
    strategies.append(sb9_result)
    
    # Check ADU eligibility
    adu_result = check_adu_eligibility(property_context)
    adu_result = generate_strategy_explanation(adu_result, retrieved_chunks, property_context)
    strategies.append(adu_result)
    
    return strategies


if __name__ == "__main__":
    # Example usage
    property_context = {
        "address": "123 Main St, San Francisco, CA",
        "city": "San Francisco",
        "zoning": "R-1",
        "lot_size_sqft": 5000,
        "existing_units": 1
    }
    
    # Mock retrieved chunks
    retrieved_chunks = [
        {
            "chunk_id": "test_1",
            "text": "ADU regulations: Minimum lot size 1200 sqft...",
            "page_start": 10,
            "page_end": 10,
            "regulation": "SF_Zoning_Code"
        }
    ]
    
    strategies = analyze_strategies(property_context, retrieved_chunks)
    
    for strategy in strategies:
        print(f"\n{strategy['strategy']}: {'ELIGIBLE' if strategy['eligible'] else 'NOT ELIGIBLE'}")
        print(f"Explanation: {strategy.get('explanation', 'N/A')[:200]}...")
