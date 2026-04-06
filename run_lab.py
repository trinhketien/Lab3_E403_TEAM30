"""
File chạy chính — So sánh Chatbot vs Agent trên 5 test cases.
Chạy: python run_lab.py
"""
import os
import sys

# Thêm thư mục gốc vào path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from src.chatbot import run_chatbot
from src.agent.agent import ReActAgent
from src.core.openai_provider import OpenAIProvider
from src.tools.shopping_tools import TOOLS

load_dotenv()


# ==============================
# 5 Test Cases
# ==============================
TEST_CASES = [
    {"type": "🟢 Chatbot OK", "query": "Laptop là gì? Khi mua laptop cần chú ý gì?"},
    {"type": "🟢 Chatbot OK", "query": "Nên mua laptop hãng nào cho sinh viên?"},
    {"type": "🔴 Agent Win", "query": "Tìm laptop dưới 16 triệu rồi so sánh 2 cái tốt nhất"},
    {"type": "🔴 Agent Win", "query": "Tìm laptop phù hợp để học lập trình, check review rồi tư vấn giúp tôi"},
    {"type": "🟡 Edge Case", "query": "Tìm máy giặt"},  # Sản phẩm không có trong database
]


def run_test(test_case: dict, mode: str):
    """Chạy 1 test case ở chế độ chatbot hoặc agent."""
    query = test_case["query"]

    if mode == "chatbot":
        result = run_chatbot(query)
        return {
            "answer": result["content"],
            "tokens": result["usage"]["total_tokens"],
            "latency_ms": result["latency_ms"],
            "steps": 1,
        }

    elif mode == "agent":
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("DEFAULT_MODEL", "gpt-4o")
        llm = OpenAIProvider(model_name=model, api_key=api_key)
        agent = ReActAgent(llm=llm, tools=TOOLS, max_steps=5)

        answer = agent.run(query)

        # Tính tổng tokens và steps từ trace
        total_tokens = sum(s["tokens"].get("total_tokens", 0) for s in agent.trace)
        total_latency = sum(s["latency_ms"] for s in agent.trace)

        return {
            "answer": answer,
            "tokens": total_tokens,
            "latency_ms": total_latency,
            "steps": len(agent.trace),
            "trace": agent.get_trace_report(),
        }


def main():
    print("=" * 70)
    print("🔬 LAB 3: CHATBOT vs ReAct AGENT — Trợ Lý Mua Sắm")
    print("=" * 70)

    results = []

    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n{'='*70}")
        print(f"📋 Test Case {i}/5: {test['type']}")
        print(f"❓ Query: {test['query']}")
        print(f"{'='*70}")

        # --- Chatbot ---
        print(f"\n🤖 [CHATBOT]")
        try:
            chatbot_result = run_test(test, "chatbot")
            print(f"💬 {chatbot_result['answer'][:300]}...")
            print(f"   ⏱️ {chatbot_result['latency_ms']}ms | 🪙 {chatbot_result['tokens']} tokens | Steps: 1")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            chatbot_result = {"answer": f"Error: {e}", "tokens": 0, "latency_ms": 0, "steps": 0}

        # --- Agent ---
        print(f"\n🤖 [AGENT]")
        try:
            agent_result = run_test(test, "agent")
            print(f"💬 {agent_result['answer'][:300]}...")
            print(f"   ⏱️ {agent_result['latency_ms']}ms | 🪙 {agent_result['tokens']} tokens | Steps: {agent_result['steps']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            agent_result = {"answer": f"Error: {e}", "tokens": 0, "latency_ms": 0, "steps": 0}

        results.append({
            "test": test,
            "chatbot": chatbot_result,
            "agent": agent_result,
        })

    # --- Bảng tổng kết ---
    print(f"\n\n{'='*70}")
    print("📊 BẢNG TỔNG KẾT")
    print(f"{'='*70}")
    print(f"{'#':<4} {'Loại':<16} {'Chat Tokens':<14} {'Agent Tokens':<14} {'Agent Steps':<12} {'Winner'}")
    print("-" * 70)

    for i, r in enumerate(results, 1):
        ct = r["chatbot"]["tokens"]
        at = r["agent"]["tokens"]
        steps = r["agent"]["steps"]
        winner = "Chatbot" if ct < at and r["test"]["type"] == "🟢 Chatbot OK" else "Agent"
        print(f"{i:<4} {r['test']['type']:<16} {ct:<14} {at:<14} {steps:<12} {winner}")


if __name__ == "__main__":
    main()
