"""
Chatbot Baseline — Gọi LLM 1 lần duy nhất, KHÔNG có tool.
Dùng làm mốc so sánh (baseline) với ReAct Agent.
"""
import os
from dotenv import load_dotenv
from src.core.openai_provider import OpenAIProvider
from src.telemetry.logger import logger

load_dotenv()

SYSTEM_PROMPT = """Bạn là trợ lý mua sắm thông minh. 
Hãy tư vấn sản phẩm dựa trên kiến thức bạn có.
Trả lời ngắn gọn, hữu ích, bằng tiếng Việt."""


def run_chatbot(user_input: str) -> dict:
    """
    Chạy chatbot baseline: 1 system prompt + 1 lần gọi LLM.
    Returns: dict chứa content, usage, latency_ms
    """
    logger.log_event("CHATBOT_START", {"input": user_input})

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("DEFAULT_MODEL", "gpt-4o")

    llm = OpenAIProvider(model_name=model, api_key=api_key)
    result = llm.generate(user_input, system_prompt=SYSTEM_PROMPT)

    logger.log_event("CHATBOT_END", {
        "output": result["content"][:200],  # Log 200 ký tự đầu
        "usage": result["usage"],
        "latency_ms": result["latency_ms"]
    })

    return result


# Chạy trực tiếp để test
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 CHATBOT BASELINE — Trợ Lý Mua Sắm")
    print("=" * 60)

    test_queries = [
        "Laptop nào tốt dưới 20 triệu để học lập trình?",
        "So sánh MacBook Air M2 với Lenovo ThinkPad E14",
    ]

    for query in test_queries:
        print(f"\n📝 User: {query}")
        result = run_chatbot(query)
        print(f"🤖 Chatbot: {result['content']}")
        print(f"   ⏱️ {result['latency_ms']}ms | 🪙 {result['usage']['total_tokens']} tokens")
        print("-" * 60)
