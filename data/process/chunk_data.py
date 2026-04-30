from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def chunk_docs(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)

    lc_docs = [
        Document(page_content=d["text"], metadata=d["meta"])
        for d in docs
    ]

    return splitter.split_documents(lc_docs)