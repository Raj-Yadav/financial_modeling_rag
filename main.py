from data.fetch.fmp_client import fetch_all
from data.transform.transform_data import build_documents
from data.process.chunk_data import chunk_docs
from db.vector_store import create_vector_db
from rag.retriever import get_retriever
from rag.rag_chain import build_chain

def run(symbol, question):
    raw = fetch_all(symbol)
    docs = build_documents(raw, symbol)
    chunks = chunk_docs(docs)

    db = create_vector_db(chunks)
    retriever = get_retriever(db)

    chain = build_chain(retriever)

    return chain.run(question)

if __name__ == "__main__":
    result = run("AAPL", "Generate financial report")
    print(result)