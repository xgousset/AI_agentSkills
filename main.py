import os
from dotenv import load_dotenv

load_dotenv()

backend = os.getenv("LLM_BACKEND", "ollama").strip()

if backend == "ollama":
    from langchain_ollama import ChatOllama
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama2-uncensored"),
        temperature=0
    )

else:
    raise ValueError(f"Unknown backend: {backend}")

response = llm.invoke("Quelle est la capitale de l’Albanie ? Réponds en une phrase.")
print(response.content)
