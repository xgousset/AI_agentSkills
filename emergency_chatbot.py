import os
import importlib.util
from dotenv import load_dotenv

# LangChain core
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import AIMessageChunk
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig

# LLM provider (Ollama)
from langchain_ollama import ChatOllama

# Multi-turn memory (LangGraph checkpointer)
from langgraph.checkpoint.memory import MemorySaver


def make_checkpointer():
    """In-memory by default. OPTIONAL: set CHAT_DB=path.db for memory that
    survives restarts (needs `pip install langgraph-checkpoint-sqlite`).
    A relative path is resolved against this file's folder (project root) so it
    lands in the same place regardless of the current working directory, and
    matches Flask's instance/ folder (e.g. CHAT_DB=instance/checkpoint.db)."""
    db = os.getenv("CHAT_DB", "").strip()
    if not db:
        return MemorySaver()
    if not os.path.isabs(db):
        db = os.path.join(os.path.dirname(os.path.abspath(__file__)), db)
    try:
        import sqlite3
        from langgraph.checkpoint.sqlite import SqliteSaver
        os.makedirs(os.path.dirname(db), exist_ok=True)
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


# Per-conversation manual location overrides set via the /coords command.
# Keyed by thread_id. In-memory only (cleared on server restart).
_pinned_locations = {}


def set_location(thread_id, lat, lon):
    """Pin a manual location for a conversation. where_am_i() will then return
    these coordinates instead of doing IP geolocation, so the model cannot drift
    back to the (often wrong) IP-based location."""
    _pinned_locations[thread_id] = {"lat": lat, "lon": lon}


def _thread_of(config):
    """Extract the thread_id LangGraph injects into a tool's RunnableConfig."""
    if not config:
        return None
    return config.get("configurable", {}).get("thread_id")


@tool
def where_am_i(config: RunnableConfig = None) -> dict:
    """Get the user's current location (latitude, longitude, city). Returns the
    location the user pinned with /coords if set, otherwise their public-IP location.
    Call this FIRST whenever you need coordinates and the user has not given them."""
    pinned = _pinned_locations.get(_thread_of(config))
    if pinned:
        return {"lat": pinned["lat"], "lon": pinned["lon"],
                "city": None, "source": "user-set (/coords)"}
    
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

# Optional extra tools (more skills). Fully isolated: if extra_tools.py is deleted
# or fails to import, we just keep the 4 base tools above — nothing else breaks.
try:
    from extra_tools import EXTRA_TOOLS
    tools += EXTRA_TOOLS
    print(f"[extra tools loaded: {[t.name for t in EXTRA_TOOLS]}]")
except Exception as e:
    print(f"[extra tools disabled: {e}]")

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


COORDS_USAGE = "usage: /coords <lat> <lon>   e.g. /coords 47.24 6.02"


def new_thread_id():
    """Generate a fresh conversation id (used by /reset and the web 'new chat')."""
    import uuid
    return "session-" + uuid.uuid4().hex[:8]


def parse_command(text):
    """Parse a leading /command into a UI-agnostic intent so both the CLI and the
    web layer share the exact same behavior.

    Returns (kind, payload):
      ("none",   None)          -> not a command; send `text` to the model as-is
      ("help",   None)          -> caller should show help
      ("reset",  None)          -> caller should start a fresh conversation
      ("coords", (lat, lon))    -> caller should pin this location (floats)
      ("error",  message)       -> caller should show this usage/error message
    """
    if not text.startswith("/"):
        return ("none", None)
    parts = text.split()
    cmd = parts[0].lower()
    if cmd == "/help":
        return ("help", None)
    if cmd == "/reset":
        return ("reset", None)
    if cmd == "/coords":
        if len(parts) != 3:
            return ("error", f"[{COORDS_USAGE}]")
        try:
            lat, lon = float(parts[1]), float(parts[2])
        except ValueError:
            return ("error", f"[{COORDS_USAGE}]")
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return ("error", "[coordinates out of range: lat -90..90, lon -180..180]")
        return ("coords", (lat, lon))
    return ("error", f"[unknown command: {cmd}] type /help")


def print_help():
    print("Commands:")
    print("  /help              show this help")
    print("  /reset             start a fresh conversation (forget history)")
    print("  /coords <lat> <lon>  set your location manually (skip IP lookup)")
    print("  quit / exit / salir  leave")


def run_cli():
    # Simplifié pour le support multi-modèle
    print("\n=== EMERGENCY ASSISTANT (CLI) ===")
    thread_id = "cli-session"
    while True:
        user = input("you> ").strip()
        if user.lower() in {"", "quit", "exit", "salir"}:
            print("Stay safe.")
            break

        # --- control commands (shared logic with the web layer) ---
        if user.startswith("/"):
            kind, payload = parse_command(user)
            if kind == "help":
                print_help()
                continue
            if kind == "reset":
                thread_id = new_thread_id()
                print(f"[new conversation: {thread_id}]")
                continue
            if kind == "error":
                print(payload)
                continue
            if kind == "coords":
                lat, lon = payload
                set_location(thread_id, lat, lon)
                print(f"[location pinned to {lat}, {lon} — where_am_i will use this]")
                continue

        print("bot> ", end="")
        for token in iter_response_tokens(user, thread_id):
            print(token, end="", flush=True)
        print()

if __name__ == "__main__":
    run_cli()
