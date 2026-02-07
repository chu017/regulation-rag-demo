"""
Streamlit demo application for regulation RAG MVP.

User workflow:
1. User inputs the address
2. System provides the address property information
3. Chatbot: user can input questions as text
4. System uses property info + user question to query the embedding store and generate an answer
5. Answer is shown with evidence traceback (source file, page, line) from original PDF sources
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.parcelz_property_api import get_property_info_from_address
from scripts.retrieve import retrieve
from scripts.answer_question import answer_question


def main():
    st.set_page_config(
        page_title="Regulation RAG Demo",
        page_icon="🏠",
        layout="wide"
    )

    st.title("🏠 Real Estate Regulation AI RAG MVP")
    st.markdown("Enter an address to get property information, then ask questions about regulations.")

    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        top_k = st.slider("Number of regulation chunks to retrieve", 5, 15, 8)
        st.markdown("---")
        st.markdown("### About")
        st.markdown("Ask questions about development regulations for your property. Answers are grounded in local regulation PDFs with source citations.")
        st.markdown("**Disclaimer:** This is a demo tool and does not constitute legal advice.")

    # ----- Step 1: Address input -----
    st.subheader("1. Enter property address")
    address = st.text_input(
        "Property Address",
        placeholder="e.g., 123 Main St, San Francisco, CA 94102",
        help="Enter a Bay Area property address",
        key="address_input"
    )

    if st.button("Get property information", type="primary", key="btn_lookup"):
        if not address or not address.strip():
            st.error("Please enter a property address")
        else:
            with st.spinner("Looking up property..."):
                try:
                    property_info = get_property_info_from_address(address.strip())
                    st.session_state["property_info"] = property_info
                    st.session_state["address_done"] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error looking up property: {e}")
                    st.exception(e)

    # ----- Step 2: Show property information -----
    if st.session_state.get("address_done") and st.session_state.get("property_info"):
        property_info = st.session_state["property_info"]
        st.subheader("2. Property information")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("City", property_info.get("city") or "Unknown")
        with col2:
            st.metric("Zoning", property_info.get("zoning") or "Unknown")
        with col3:
            lot = property_info.get("lot_size_sqft")
            st.metric("Lot size", f"{lot:,} sqft" if lot is not None else "—")
        with st.expander("View full property details", expanded=False):
            st.json(property_info)

        # ----- Step 3 & 4 & 5: Chatbot — question input, retrieve + generate, show answer with evidence -----
        st.subheader("3. Ask a question about regulations")
        st.markdown("Ask anything about development rules for this property (e.g. *Can I build an ADU?*, *What are the setback requirements?*). The system will use the property info and your question to search the regulation index and generate an answer with source citations.")

        user_question = st.text_input(
            "Your question",
            placeholder="e.g., Can I build an ADU on this lot? What are the height limits?",
            key="user_question_input"
        )

        if st.button("Get answer", type="primary", key="btn_answer"):
            if not user_question or not user_question.strip():
                st.warning("Please enter a question")
            else:
                with st.spinner("Searching regulations and generating answer..."):
                    try:
                        # Build query from property context + user question for retrieval
                        city = property_info.get("city") or ""
                        zoning = property_info.get("zoning") or ""
                        query = f"{user_question} Regulations for {zoning} zoning in {city}. {user_question}"

                        retrieved_chunks = retrieve(
                            query_text=query,
                            city=property_info.get("city"),
                            zoning=property_info.get("zoning"),
                            top_k=top_k
                        )

                        if not retrieved_chunks:
                            st.warning("No relevant regulation chunks found for this property. Try a different question or ensure the index has been built with data for this city.")
                        else:
                            # Generate answer using property + question + chunks
                            result = answer_question(property_info, user_question.strip(), retrieved_chunks)

                            st.subheader("Answer")
                            st.markdown(result["answer"])

                            # Evidence traceback: source file, page, line from original PDF
                            st.subheader("Evidence (traceback to source)")
                            st.markdown("Sources used to generate the answer, with file name, page, and line references from the original PDF data:")
                            for i, ev in enumerate(result["evidence"], 1):
                                page_str = f"Page {ev['page_start']}" if ev.get('page_start') == ev.get('page_end') else f"Pages {ev['page_start']}-{ev['page_end']}"
                                line_str = ""
                                if ev.get("line_start") is not None and ev.get("line_end") is not None:
                                    line_str = f", Lines {ev['line_start']}-{ev['line_end']}"
                                with st.expander(f"**{ev.get('source_file', 'Unknown')}** — {page_str}{line_str}", expanded=False):
                                    st.caption(f"Chunk ID: {ev.get('chunk_id', '—')}")
                                    st.text(ev.get("text", "") or "(no excerpt)")
                            st.session_state["last_answer"] = result
                            st.session_state["last_question"] = user_question.strip()
                    except Exception as e:
                        st.error(f"Error generating answer: {e}")
                        st.exception(e)

        # Optional: show last Q&A in session
        if st.session_state.get("last_answer") and st.session_state.get("last_question"):
            with st.expander("View last question and answer", expanded=False):
                st.markdown(f"**Q:** {st.session_state['last_question']}")
                st.markdown(f"**A:** {st.session_state['last_answer']['answer']}")

        st.markdown("---")
        if st.button("Clear property and start over", key="btn_clear"):
            for key in ("property_info", "address_done", "last_answer", "last_question"):
                st.session_state.pop(key, None)
            st.rerun()

    # Instructions
    with st.expander("📖 How to use", expanded=False):
        st.markdown("""
1. **Enter address** — Type a property address and click **Get property information**.
2. **Review property info** — City, zoning, and lot size are shown (from Parcelz when available).
3. **Ask a question** — In the text box, ask anything about regulations for this property (e.g. ADU, setbacks, height limits).
4. **Get answer** — The system combines your question and the property info to search the regulation index, then generates an answer.
5. **Evidence** — Each answer includes evidence traceback: **source file name**, **page**, and **line** from the original PDF sources.

**Setup:** Build the FAISS index with `python scripts/embed_index.py`, add regulation PDFs under `data/raw/{city}/`, and set `GEMINI_API_KEY` in `.env`.
        """)


if __name__ == "__main__":
    main()
