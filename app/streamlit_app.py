import streamlit as st
from main import run

st.title("📊 Financial RAG Report Generator")

symbol = st.text_input("Enter Stock Symbol", "AAPL")

if st.button("Generate Report"):
    with st.spinner("Generating..."):
        result = run(symbol, "Generate financial report")
        st.write(result)