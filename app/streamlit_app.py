import sys
import os
import streamlit as st
import transformers

# Silence Hugging Face warnings
transformers.logging.set_verbosity_error()

# 1. Get the absolute path to the parent directory (project root)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# 2. Add the project root to sys.path
sys.path.append(parent_dir)

# 3. Now you can perform an absolute import from main.py
from main import run

st.title("📊 Financial RAG Report Generator")

symbol = st.text_input("Enter Stock Symbol", "AAPL")

if st.button("Generate Report"):
    with st.spinner("Generating..."):
        result = run(symbol, "Generate financial report")
        st.write(result)