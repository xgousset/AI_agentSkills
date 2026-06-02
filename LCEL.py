""" LCEL : composer prompt | llm | parser avec l’opé rateur pipe ."""
import os
from dotenv import load_dotenv
from langchain_core . prompts import ChatPromptTemplate
from langchain_core . output_parsers import StrOutputParser

load_dotenv ()
backend = os . getenv (" LLM_BACKEND ", " else ")

if backend == " mistral ":
    from langchain_mistralai import ChatMistralAI
    llm = ChatMistralAI ( model =" mistral -small - latest ", temperature =0.7)
else :
    from langchain_ollama import ChatOllama
    llm = ChatOllama ( model = os . getenv (" OLLAMA_MODEL ", " llama2-uncensored") , temperature =0.7)

prompt = ChatPromptTemplate . from_template (
" Raconte -moi une blague courte sur le sujet : { sujet }"
)

chain = prompt | llm | StrOutputParser ()

for sujet in [" les pompiers ", " les data scientists "]:
    print (f" --- { sujet } ---")
    print ( chain . invoke ({" sujet ": sujet }) )