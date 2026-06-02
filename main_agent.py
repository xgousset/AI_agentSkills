import os
from dotenv import load_dotenv

# LangChain core
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, AIMessageChunk

# LLM provider (Ollama)
from langchain_ollama import ChatOllama

load_dotenv()

backend = os.getenv("LLM_BACKEND", "ollama").strip()

if backend != "ollama":
    raise ValueError(f"Unknown backend: {backend}")

# Create the LLM (Ollama)
llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
    temperature=0
)

# Define tools
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b

@tool
def greet(name: str) -> str:
    """Return a friendly greeting."""
    return f"Hello {name}, nice to meet you!"

tools = [multiply, greet]

# Create the agent
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a funny french mocker assistant. Use tools when needed.",
)

# Use the agent
print("\n=== AGENT EXECUTION ===\n")

# Example of an ideal prompt (shown so the user knows the expected format)
EXAMPLE_PROMPT = """You must:
1. Greet a person named Jared.
2. Compute 12 × 7.
3. Compute the square of 15.
4. Then summarize everything in one final sentence."""

print("Example of an ideal prompt:")
print(EXAMPLE_PROMPT)
print("\nEnter your prompt (leave empty to use the example above):")
query = input("> ").strip()

if not query:
    query = EXAMPLE_PROMPT

# Stream token by token, but only the model's text (skip tool output / tool_calls)
# recursion_limit caps the loop so a weak model can't spin forever
print("=== FINAL ANSWER ===")
try:
    for token, metadata in agent.stream(
        {"messages": [{"role": "user", "content": query}]},
        stream_mode="messages",
        config={"recursion_limit": 10},
    ):
        # AIMessageChunk = the model's own output; .content empty when it's a tool_call step
        if isinstance(token, AIMessageChunk) and token.content:
            print(token.content, end="", flush=True)
    print()
except Exception as e:
    print(f"\n[stopped: {type(e).__name__}] model looped without a final answer.")
