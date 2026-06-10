import os
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import AIMessageChunk
from langgraph.checkpoint.memory import MemorySaver

@tool
def get_test_info() -> str:
    """Returns test info."""
    return "Test tool works"

def test_model(model_name, model_key):
    print(f"\n--- Testing model: {model_name} ({model_key}) ---")
    try:
        llm = ChatOllama(model=model_name, temperature=0)
        checkpointer = MemorySaver()
        agent = create_agent(
            model=llm,
            tools=[get_test_info],
            system_prompt="You are a helpful assistant.",
            checkpointer=checkpointer,
        )
        
        config = {"configurable": {"thread_id": "test-thread"}, "recursion_limit": 5}
        
        print("Invoking agent...")
        for token, metadata in agent.stream(
            {"messages": [{"role": "user", "content": "Hello! Use the tool please."}]},
            stream_mode="messages",
            config=config,
        ):
            if isinstance(token, AIMessageChunk) and token.content:
                print(token.content, end="", flush=True)
        print("\nSuccess!")
    except Exception as e:
        print(f"\nFAILED: {type(e).__name__}: {e}")

if __name__ == "__main__":
    models = {
        "qwen": "qwen2.5:3b",
        "mistral": "mistral:latest",
        "llama2": "llama2-uncensored:latest",
        "deepseek": "deepseek-r1:1.5b"
    }
    for key, name in models.items():
        test_model(name, key)
