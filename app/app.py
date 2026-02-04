"""
Streamlit demo application for regulation RAG MVP.
Features:
- Address input
- Strategy analysis
- Constraints table
- Source citations with expandable sections
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.property_api import get_property_info_from_address
from scripts.retrieve import retrieve
from scripts.strategy import analyze_strategies


def main():
    st.set_page_config(
        page_title="Regulation RAG Demo",
        page_icon="🏠",
        layout="wide"
    )
    
    st.title("🏠 Real Estate Regulation AI RAG MVP")
    st.markdown("Enter a Bay Area address to analyze development strategies (SB9, ADU)")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        top_k = st.slider("Number of regulation chunks to retrieve", 5, 15, 8)
        st.markdown("---")
        st.markdown("### About")
        st.markdown("This demo analyzes property development strategies based on local regulations.")
        st.markdown("**Disclaimer:** This is a demo tool and does not constitute legal advice.")
    
    # Main input
    address = st.text_input(
        "Property Address",
        placeholder="e.g., 123 Main St, San Francisco, CA 94102",
        help="Enter a Bay Area property address"
    )
    
    if st.button("Analyze Property", type="primary"):
        if not address:
            st.error("Please enter a property address")
            return
        
        with st.spinner("Analyzing property..."):
            try:
                # Step 1: Get property information
                st.subheader("Step 1: Property Information")
                property_info = get_property_info_from_address(address)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("City", property_info.get("city", "Unknown"))
                with col2:
                    st.metric("Zoning", property_info.get("zoning", "Unknown"))
                with col3:
                    st.metric("Lot Size", f"{property_info.get('lot_size_sqft', 0):,} sqft")
                
                st.json(property_info)
                
                # Step 2: Retrieve relevant regulations
                st.subheader("Step 2: Retrieving Relevant Regulations")
                query = f"development regulations for {property_info.get('zoning', 'residential')} zoning in {property_info.get('city', 'city')}"
                
                retrieved_chunks = retrieve(
                    query_text=query,
                    city=property_info.get("city"),
                    zoning=property_info.get("zoning"),
                    top_k=top_k
                )
                
                if not retrieved_chunks:
                    st.warning("No relevant regulations found. Please ensure the index has been built with data for this city.")
                    return
                
                st.success(f"Retrieved {len(retrieved_chunks)} relevant regulation chunks")
                
                # Step 3: Analyze strategies
                st.subheader("Step 3: Strategy Analysis")
                strategies = analyze_strategies(property_info, retrieved_chunks)
                
                # Display strategies
                for strategy in strategies:
                    strategy_name = strategy.get("strategy", "Unknown")
                    is_eligible = strategy.get("eligible", False)
                    
                    # Strategy summary card
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            status_emoji = "✅" if is_eligible else "❌"
                            status_text = "ELIGIBLE" if is_eligible else "NOT ELIGIBLE"
                            st.markdown(f"### {status_emoji} {strategy_name}: {status_text}")
                            st.markdown(f"*{strategy.get('description', '')}*")
                        with col2:
                            st.metric("Status", status_text)
                        
                        # Hard rules
                        st.markdown("#### Hard Rules Check")
                        hard_rules = strategy.get("hard_rules", [])
                        for rule in hard_rules:
                            rule_emoji = "✅" if is_eligible and "Meets" in rule else "⚠️"
                            st.markdown(f"{rule_emoji} {rule}")
                        
                        # LLM Explanation
                        st.markdown("#### Regulatory Analysis")
                        explanation = strategy.get("explanation", "No explanation available")
                        st.markdown(explanation)
                        
                        # Constraints table
                        st.markdown("#### Constraints & Requirements")
                        citations = strategy.get("citations", [])
                        if citations:
                            constraints_data = []
                            for citation in citations:
                                constraints_data.append({
                                    "Regulation": citation.get("regulation", "Unknown"),
                                    "Pages": f"{citation.get('page_start', '?')}-{citation.get('page_end', '?')}",
                                    "Chunk ID": citation.get("chunk_id", "Unknown")
                                })
                            
                            st.dataframe(constraints_data, use_container_width=True)
                        else:
                            st.info("No citations available")
                        
                        # Expandable source citations
                        with st.expander("📄 View Source Citations", expanded=False):
                            for i, citation in enumerate(citations, 1):
                                st.markdown(f"**Citation {i}:**")
                                st.markdown(f"- **Regulation:** {citation.get('regulation', 'Unknown')}")
                                st.markdown(f"- **Pages:** {citation.get('page_start', '?')} - {citation.get('page_end', '?')}")
                                st.markdown(f"- **Chunk ID:** {citation.get('chunk_id', 'Unknown')}")
                                
                                # Find and display the actual text
                                chunk_id = citation.get("chunk_id")
                                matching_chunk = next(
                                    (c for c in retrieved_chunks if c.get("chunk_id") == chunk_id),
                                    None
                                )
                                if matching_chunk:
                                    with st.container():
                                        st.markdown("**Relevant Text:**")
                                        st.text_area(
                                            f"Text from {chunk_id}",
                                            matching_chunk.get("text", ""),
                                            height=200,
                                            key=f"text_{chunk_id}",
                                            label_visibility="collapsed"
                                        )
                                
                                st.markdown("---")
                        
                        st.markdown("---")
                
                # Raw data expander
                with st.expander("🔍 View Raw Data", expanded=False):
                    st.json({
                        "property_info": property_info,
                        "retrieved_chunks_count": len(retrieved_chunks),
                        "strategies": strategies
                    })
                
            except Exception as e:
                st.error(f"Error analyzing property: {e}")
                st.exception(e)
    
    # Instructions
    with st.expander("📖 How to Use", expanded=False):
        st.markdown("""
        1. **Enter Address**: Type a Bay Area property address
        2. **Click Analyze**: The system will:
           - Look up property information (city, zoning, lot size)
           - Retrieve relevant regulation chunks
           - Analyze SB9 and ADU eligibility
           - Generate explanations with citations
        3. **Review Results**: 
           - Check strategy eligibility status
           - Read regulatory analysis
           - View source citations
           - Expand citations to see original regulation text
        
        **Note**: This is a demo. Ensure you have:
        - Built the FAISS index (run `python scripts/embed_index.py`)
        - Added regulation PDFs to `data/raw/{city}/`
        - Set `GEMINI_API_KEY` in `.env` file
        """)


if __name__ == "__main__":
    main()
