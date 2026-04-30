from langchain_ollama import ChatOllama

# Connect to the container
llm = ChatOllama(model="falcon:7b", base_url="http://localhost:11434")

print("Sending prompt to local Falcon-7B model...")
response = llm.invoke("What is the capital of France? Answer in one sentence.")

print("\nResponse:")
print(response.content)