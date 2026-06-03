import os
import importlib.util
from dotenv import load_dotenv

# LangChain core
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import AIMessageChunk

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

backend = os.getenv("LLM_BACKEND", "ollama").strip()

if backend != "ollama":
    raise ValueError(f"Unknown backend: {backend}")

# Create the LLM (Ollama) - same config as main_agent.py
llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
    temperature=0
)

# Reuse the project's real skill scripts (single source of truth)
# Load each script module by path so the .gemini/skills/ scripts stay the only copy.
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


# Tools: thin wrappers that summarize so the model isn't flooded with raw JSON
@tool
def where_am_i() -> dict:
    """Get the user's current location (latitude, longitude, city) from their public IP.
    Call this FIRST whenever you need coordinates and the user has not given them."""
    return _location.get_location()


def _summarize_pois(data, radius_km):
    """Turn raw Overpass JSON into a short text summary (count + first few names)."""
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

# Pick memory backend (in-memory, or persistent if CHAT_DB is set)
checkpointer = make_checkpointer()

# Create the agent with conversational memory
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are a calm emergency operator assisting someone during a nuclear crisis. "
        "Answer concisely and clearly. Always reply in the SAME language the user writes in. "
        "If you need the user's location and they have not "
        "given it, call where_am_i FIRST, then reuse those coordinates with the other tools. "
        "Never invent coordinates."
    ),
    checkpointer=checkpointer,
)

# Chat loop
DEFAULT_THREAD_ID = "session-1"
thread_id = DEFAULT_THREAD_ID  # mutable: /reset starts a fresh conversation

def make_config(current_thread_id=None):
    return {"configurable": {"thread_id": current_thread_id or thread_id}, "recursion_limit": 10}


def iter_response_tokens(user_message, current_thread_id=None):
    for token, metadata in agent.stream(
        {"messages": [{"role": "user", "content": user_message}]},
        stream_mode="messages",
        config=make_config(current_thread_id),
    ):
        if isinstance(token, AIMessageChunk) and token.content:
            yield token.content


COORDS_USAGE = "usage: /coords <lat> <lon>   e.g. /coords 47.24 6.02"


def new_thread_id():
    """Generate a fresh conversation id (used by /reset and the web 'new chat')."""
    import uuid
    return "session-" + uuid.uuid4().hex[:8]


def parse_command(text):
    """Parse a leading /command into a UI-agnostic intent so both the CLI and the
    web layer share the exact same behavior.

    Returns (kind, payload):
      ("none",  None)            -> not a command; send `text` to the model as-is
      ("help",  None)            -> caller should show help
      ("reset", None)            -> caller should start a fresh conversation
      ("send",  rewritten_text)  -> send this rewritten message to the model
      ("error", message)         -> caller should show this usage/error message
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
        lat, lon = parts[1], parts[2]
        return ("send", (
            f"My current location is latitude {lat}, longitude {lon}. "
            "Remember it for the rest of this conversation."
        ))
    return ("error", f"[unknown command: {cmd}] type /help")


def print_help():
    print("Commands:")
    print("  /help              show this help")
    print("  /reset             start a fresh conversation (forget history)")
    print("  /coords <lat> <lon>  set your location manually (skip IP lookup)")
    print("  quit / exit / salir  leave")


def run_cli():
    global thread_id

    print("\n=== EMERGENCY ASSISTANT (type '/help' for commands, 'quit' to exit) ===")
    print("Try: 'Where am I and where are the nearest shelters?'")
    print("     'And the closest pharmacies?'   /   'Which way would fallout drift?'\n")

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
            if kind == "send":
                # /coords: send the rewritten message to the model below
                user = payload
                print("[location noted]")

        print("bot> ", end="")
        try:
            for token_text in iter_response_tokens(user, thread_id):
                print(token_text, end="", flush=True)
            print()
        except Exception as e:
            print(f"\n[stopped: {type(e).__name__}] model looped without a final answer.")


if __name__ == "__main__":
    run_cli()
