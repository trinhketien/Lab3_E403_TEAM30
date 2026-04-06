"""
Demo tương tác — Gõ câu hỏi, xem Chatbot vs Agent trả lời.
Chạy: python demo.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from src.chatbot import run_chatbot
from src.agent.agent import ReActAgent
from src.core.openai_provider import OpenAIProvider
from src.tools.shopping_tools import TOOLS

load_dotenv()


def main():
    print("=" * 60)
    print("  DEMO: Chatbot vs Agent - Tro Ly Mua Sam")
    print("=" * 60)
    print("Go cau hoi de thu. Goi 'quit' de thoat.")
    print("Go 'chatbot' hoac 'agent' de chon che do.")
    print("Mac dinh: chay CA HAI de so sanh.")
    print("-" * 60)

    mode = "both"  # both / chatbot / agent

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("DEFAULT_MODEL", "gpt-4o")

    while True:
        print(f"\n[Mode: {mode}]")
        user_input = input("Ban hoi: ").strip()

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Tam biet!")
            break
        if user_input.lower() in ("chatbot", "agent", "both"):
            mode = user_input.lower()
            print(f"-> Da chuyen sang mode: {mode}")
            continue

        # --- CHATBOT ---
        if mode in ("both", "chatbot"):
            print(f"\n--- CHATBOT ---")
            try:
                result = run_chatbot(user_input)
                print(f"{result['content']}")
                print(f"[{result['latency_ms']}ms | {result['usage']['total_tokens']} tokens]")
            except Exception as e:
                print(f"Loi: {e}")

        # --- AGENT ---
        if mode in ("both", "agent"):
            print(f"\n--- AGENT ---")
            try:
                llm = OpenAIProvider(model_name=model, api_key=api_key)
                agent = ReActAgent(llm=llm, tools=TOOLS, max_steps=5)
                answer = agent.run(user_input)
                print(f"{answer}")

                total_tokens = sum(s["tokens"].get("total_tokens", 0) for s in agent.trace)
                total_ms = sum(s["latency_ms"] for s in agent.trace)
                print(f"[{total_ms}ms | {total_tokens} tokens | {len(agent.trace)} steps]")
            except Exception as e:
                print(f"Loi: {e}")

        print("-" * 60)


if __name__ == "__main__":
    main()
