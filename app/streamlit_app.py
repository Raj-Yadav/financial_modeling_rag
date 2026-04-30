import sys
import os
import streamlit as st
import transformers

# Silence Hugging Face warnings
transformers.logging.set_verbosity_error()

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir  = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from main import run

st.title("📊 Financial RAG Report Generator")

symbol = st.text_input("Enter Stock Symbol", "AAPL")

col1, col2 = st.columns(2)
with col1:
    max_age_hours = st.slider(
        "⏱️ Cache max age (hours)",
        min_value=1, max_value=168, value=24,
        help="If data is younger than this, SQLite is used and the API is skipped."
    )
with col2:
    force_refresh = st.checkbox(
        "🔄 Force refresh from API",
        value=False,
        help="Ignore cache and always fetch fresh data from the API."
    )

if st.button("Generate Report"):
    with st.spinner("Loading data & generating report..."):
        result = run(
            symbol,
            "Generate financial report",
            max_age_hours=max_age_hours,
            force_refresh=force_refresh,
        )
        st.success("✅ Done")
        st.write(result)