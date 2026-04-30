from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from rag.prompt_templates import PROMPT

def build_chain(retriever):
    llm = ChatOllama(
        model="falcon:7b",
        temperature=0.2,
        base_url="http://localhost:11434"
    )

    # Use ChatPromptTemplate instead of PromptTemplate
    prompt = ChatPromptTemplate.from_template(PROMPT)
    
    # This combination replaces the old RetrievalQA
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, combine_docs_chain)
