from data.fetch.fmp_client import fetch_all
from data.transform.transform_data import build_documents
from data.process.chunk_data import chunk_docs
from db.vector_store import create_vector_db
from db.storage import save_raw_data, is_data_fresh, load_raw_from_sqlite
from rag.retriever import get_retriever
from rag.rag_chain import build_chain
import transformers

# Silence Hugging Face warnings
transformers.logging.set_verbosity_error()


def run(symbol, question, max_age_hours: int = 24, force_refresh: bool = False):
    """
    Full RAG pipeline with SQLite cache-first data loading.

    Parameters
    ----------
    symbol        : stock ticker, e.g. "AAPL"
    question      : natural-language prompt for the LLM
    max_age_hours : hours before cached data is considered stale (default 24)
    force_refresh : if True, always fetch from API even if cache is fresh
    """
    symbol = symbol.upper()

    # 1. Cache-first: read from SQLite if fresh, else hit the API
    if not force_refresh and is_data_fresh(symbol, max_age_hours=max_age_hours):
        print(f"[pipeline] ✅ Cache hit — loading '{symbol}' from SQLite (skipping API call)")
        raw = load_raw_from_sqlite(symbol)
    else:
        print(f"[pipeline] 🌐 Cache miss — fetching '{symbol}' from FMP API")
        raw = fetch_all(symbol)
        save_raw_data(raw, symbol)

    # 2. Transform → chunk → embed → retrieve → generate
    docs      = build_documents(raw, symbol)
    chunks    = chunk_docs(docs)
    db        = create_vector_db(chunks)
    retriever = get_retriever(db)
    chain     = build_chain(retriever)

    return chain.invoke({"input": question})


if __name__ == "__main__":
    result = run("AAPL", "Generate financial report")
    print(result)