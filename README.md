# Financial Modeling RAG

A Retrieval-Augmented Generation pipeline that generates structured financial
reports for any publicly traded stock using real market data and a local LLM.

flowchart TD
    A([" User — Streamlit UI \nEnter stock symbol + cache settings"])

    subgraph CACHE["Cache-first check"]
        B{"is_data_fresh?\n SQLite lookup"}
    end

    subgraph FETCH["Data layer — FMP API"]
        D["fetch_all\nprofile · metrics · ratios · price"]
        E["save_raw_data\nWrite to financial_data.db"]
    end

    subgraph DB["SQLite — financial_data.db"]
        C[("profile\nmetrics\nratios\nprice_history")]
    end

    subgraph TRANSFORM["Transform & chunk"]
        F["build_documents\nFlattens JSON → text docs"]
        G["chunk_docs\nRecursiveCharacterTextSplitter\nchunk=300 · overlap=50"]
    end

    subgraph VECTOR["Embedding & retrieval"]
        H["create_vector_db\nFAISS + all-MiniLM-L6-v2"]
        I["get_retriever\nTop-5 relevant chunks"]
    end

    subgraph LLM["Generation — Ollama"]
        J["build_chain\nfalcon:7b · temp 0.2\nFinancial analyst prompt"]
    end

    K([" Report\nOverview · Performance · Risks · Conclusion "])

    A --> B
    B -- "Cache hit\n(data fresh)" --> C
    B -- "Cache miss\nor force refresh" --> D
    D --> E --> C
    C --> F --> G --> H --> I --> J --> K

## How it works

1. **Fetch** — Pulls company profile, key metrics, financial ratios, and
   historical price data from the Financial Modeling Prep (FMP) API.
2. **Cache** — Raw data is persisted to a local SQLite database
   (`db/financial_data.db`). On subsequent runs, if the data is younger than
   `max_age_hours` (default 24h), the API call is skipped entirely.
3. **Transform** — JSON responses are flattened into plain-text narrative
   chunks (e.g. "AAPL moved +8.2% in the last 30 days").
4. **Chunk** — Text is split into 300-token chunks with 50-token overlap using
   LangChain's `RecursiveCharacterTextSplitter`.
5. **Embed & store** — Chunks are embedded with
   `sentence-transformers/all-MiniLM-L6-v2` and indexed in a FAISS vector
   store.
6. **Retrieve** — The top-5 most relevant chunks are fetched for the query.
7. **Generate** — A local Ollama `falcon:7b` model produces a structured
   financial report (Overview, Performance, Market Trend, Risks, Conclusion).

## Stack

| Layer | Technology |
|---|---|
| Data source | Financial Modeling Prep API |
| Storage | SQLite (`financial_data.db`) |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| Vector store | FAISS |
| Framework | LangChain |
| LLM | Ollama `falcon:7b` (local) |
| UI | Streamlit |

## Project structure
financial_modeling_rag/
├── app/streamlit_app.py        # Web UI
├── data/
│   ├── fetch/fmp_client.py     # FMP API client
│   ├── transform/transform_data.py  # JSON → text docs
│   └── process/chunk_data.py   # Text splitting
├── db/
│   ├── storage.py              # SQLite read/write + cache logic
│   └── vector_store.py         # FAISS vector DB
├── rag/
│   ├── rag_chain.py            # LangChain RAG chain
│   ├── retriever.py            # Top-k retriever
│   └── prompt_templates.py     # Financial analyst prompt
├── utils/config.py             # API key loading (.env)
├── main.py                     # Pipeline entry point
└── requirements.txt


## Setup

```bash
pip install -r requirements.txt

# Pull the LLM (requires Ollama installed)
ollama pull falcon:7b
```

Create a `.env` file:
FMP_API_KEY=your_key_here

## Run

```bash
# CLI
python main.py

# Web UI
streamlit run app/streamlit_app.py
```

## Environment variables

| Variable | Description |
|---|---|
| `FMP_API_KEY` | Financial Modeling Prep API key |
| `OPENAI_API_KEY` | Optional — not used in current pipeline |