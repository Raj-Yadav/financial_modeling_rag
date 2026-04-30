from langchain.chains import RetrievalQA

from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate

from rag.prompt_templates import PROMPT

def build_chain(retriever):
    # Connect to the local Docker container running Ollama
    llm = ChatOllama(
        model="falcon:7b",
        temperature=0.2,
        base_url="http://localhost:11434" # This is the port Docker exposed!
    )

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=PROMPT
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt}
    )