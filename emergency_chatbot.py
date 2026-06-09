import os
import importlib.util
from dotenv import load_dotenv

# LangChain core
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import AIMessageChunk
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# LLM provider (Ollama)
from langchain_ollama import ChatOllama

# Multi-turn memory (LangGraph checkpointer)
from langgraph.checkpoint.memory import MemorySaver


def make_checkpointer():
    """In-memory by default. OPTIONAL: set CHAT_DB=path.db for memory that
    survives restarts (needs `pip install langgraph-checkpoint-sqlite`)."""
    db = os.getenv("CHAT_DB", "").strip()
    if not db:
        return MemorySaver()
    try:
        import sqlite3
        from langgraph.checkpoint.sqlite import SqliteSaver
        conn = sqlite3.connect(db, check_same_thread=False)
        print(f"[persistent memory: {db}]")
        return SqliteSaver(conn)
    except Exception as e:
        print(f"[CHAT_DB set but persistent memory unavailable ({e}); using in-memory]")
        return MemorySaver()

load_dotenv()

# Pick memory backend (in-memory, or persistent if CHAT_DB is set)
checkpointer = make_checkpointer()

# Available models (Restricted to tool-compatible models for stability)
AVAILABLE_MODELS = {
    "qwen": os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
    "mistral": "mistral:latest"
}

# Cache for agents to avoid recreating them
_agent_cache = {}

def get_llm(model_key="qwen"):
    model_name = AVAILABLE_MODELS.get(model_key, AVAILABLE_MODELS["qwen"])
    return ChatOllama(model=model_name, temperature=0)

# Reuse the project's real skill scripts (single source of truth)
SKILLS = os.path.join(os.path.dirname(__file__), ".gemini", "skills")

def _load(skill, script):
    path = os.path.join(SKILLS, skill, "scripts", script)
    spec = importlib.util.spec_from_file_location(f"_skill_{skill}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

_location = _load("location-provider", "get_location.py")
_shelters = _load("survival-strategist", "find_shelters.py")
_resources = _load("resource-inventory", "find_resources.py")
_weather = _load("fallout-predictor", "get_weather.py")

@tool
def where_am_i() -> dict:
    """Get the user's current location (latitude, longitude, city) from their public IP.
    Call this FIRST whenever you need coordinates and the user has not given them."""
    loc = _location.get_location()
    if "error" in loc:
        return {"error": "Impossible de déterminer votre position automatiquement. Veuillez fournir votre ville ou vos coordonnées."}
    return loc

def _summarize_pois(data, radius_km):
    if not isinstance(data, dict) or "elements" not in data:
        return f"No data (got: {data})"
    elements = data["elements"]
    lines = [f"Found {len(elements)} place(s) within {radius_km} km."]
    for el in elements[:8]:
        tags = el.get("tags", {})
        name = tags.get("name", "unnamed")
        kind = tags.get("amenity") or tags.get("shop") or tags.get("building") or "?"
        lat, lon = el.get("lat"), el.get("lon")
        coords = f" ({lat}, {lon})" if lat and lon else ""
        lines.append(f"- {name} [{kind}]{coords}")
    return "\n".join(lines)

@tool
def find_shelters(lat: float, lon: float, radius_km: int = 20) -> str:
    """Find public shelters near coordinates: bomb/nuclear shelters, underground parkings,
    subway stations, hospitals/universities/government buildings. Use during a nuclear emergency."""
    return _summarize_pois(_shelters.get_shelters(lat, lon, radius_km), radius_km)

@tool
def find_supplies(lat: float, lon: float, radius_km: int = 5) -> str:
    """Find nearby survival supplies: pharmacies (potassium iodide / KI), supermarkets (food),
    and drinking-water points. Use when the user asks about supplies, food, water or medicine."""
    return _summarize_pois(_resources.get_resources(lat, lon, radius_km), radius_km)

@tool
def wind_forecast(lat: float, lon: float) -> dict:
    """Get current wind (surface + altitude layers) to predict which direction radioactive
    fallout would drift. Use when the user asks about fallout direction, wind, or where it's safe."""
    return _weather.get_wind_data(lat, lon)

tools = [where_am_i, find_shelters, find_supplies, wind_forecast]

def get_agent(model_key="qwen"):
    if model_key not in _agent_cache:
        llm = get_llm(model_key)
        
        # Specific prompt tuning for Mistral if needed, otherwise general
        prompt_text = (
            "You are a calm emergency operator assisting someone during a nuclear crisis. "
            "Answer concisely and clearly. Always reply in the SAME language the user writes in. "
            "If you need the user's location and they have not "
            "given it, call where_am_i FIRST, then reuse those coordinates with the other tools. "
            "Never invent coordinates."
        )
        
        if model_key == "mistral":
            prompt_text += " You MUST use the provided tools to get real data before answering."

        _agent_cache[model_key] = create_agent(
            model=llm,
            tools=tools,
            system_prompt=prompt_text,
            checkpointer=checkpointer,
        )
    return _agent_cache[model_key]

# --- Verification Agents ---

concordance_prompt = ChatPromptTemplate.from_template(
    "Tu es un expert en vérification de concordance. "
    "Vérifie si la réponse de l'IA correspond à la requête de l'utilisateur.\n\n"
    "Requête : {query}\n"
    "Réponse : {response}\n\n"
    "La réponse est-elle pertinente ? Réponds par OUI ou NON, puis explique brièvement pourquoi en une phrase."
)

hallucination_prompt = ChatPromptTemplate.from_template(
    "Tu es un expert en détection d'hallucinations. "
    "Vérifie si la réponse suivante contient des informations inventées ou techniquement suspectes.\n\n"
    "Réponse : {response}\n\n"
    "Y a-t-il des hallucinations ? Réponds par AUCUNE ou DÉTECTÉE, puis explique brièvement pourquoi en une phrase."
)

def verify_response(query, response, model_key="qwen"):
    llm = get_llm(model_key)
    
    concordance_chain = concordance_prompt | llm | StrOutputParser()
    hallucination_chain = hallucination_prompt | llm | StrOutputParser()
    
    concordance = concordance_chain.invoke({"query": query, "response": response})
    hallucination = hallucination_chain.invoke({"response": response})
    
    return {
        "concordance": concordance,
        "hallucination": hallucination
    }

# --- Response Generation ---

def iter_response_tokens(user_message, current_thread_id, model_key="qwen"):
    agent = get_agent(model_key)
    config = {"configurable": {"thread_id": current_thread_id}, "recursion_limit": 10}
    
    full_response = ""
    for token, metadata in agent.stream(
        {"messages": [{"role": "user", "content": user_message}]},
        stream_mode="messages",
        config=config,
    ):
        if isinstance(token, AIMessageChunk) and token.content:
            full_response += token.content
            yield token.content

    # Run verifications at the end
    # We yield a separator and then the verification results
    verif = verify_response(user_message, full_response, model_key)
    
    yield "\n\n--- VÉRIFICATIONS ---\n"
    yield f"**Concordance :** {verif['concordance']}\n"
    yield f"**Hallucination :** {verif['hallucination']}"

# --- CLI ---

def run_cli():
    # Simplifié pour le support multi-modèle
    print("\n=== EMERGENCY ASSISTANT (CLI) ===")
    while True:
        user = input("you> ").strip()
        if user.lower() in {"quit", "exit"}: break
        
        print("bot> ", end="")
        for token in iter_response_tokens(user, "cli-session"):
            print(token, end="", flush=True)
        print()

if __name__ == "__main__":
    run_cli()
