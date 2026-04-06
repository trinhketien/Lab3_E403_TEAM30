"""
ReAct Agent v1 — Vòng lặp Thought → Action → Observation.
Đây là file cốt lõi của Lab 3.
"""
import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger


class ReActAgent:
    """
    ReAct Agent: Suy luận (Thought) → Hành động (Action) → Quan sát (Observation)
    Lặp lại cho đến khi có Final Answer hoặc hết max_steps.
    """

    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.trace = []  # Ghi lại toàn bộ quá trình suy luận

    def get_system_prompt(self) -> str:
        """
        System Prompt — "Bản hướng dẫn" cho AI.
        Gồm 5 phần: Identity, Capabilities, Instructions, Constraints, Output Format.
        """
        tool_descriptions = "\n".join(
            [f"  - {t['name']}: {t['description']}" for t in self.tools]
        )

        return f"""You are a Smart Shopping Assistant. You help users find and compare products.

AVAILABLE TOOLS:
{tool_descriptions}

INSTRUCTIONS:
You MUST follow this exact format for EVERY response:

Thought: [Your reasoning about what to do next]
Action: [tool_name("argument")]

After receiving an Observation, continue with another Thought/Action if needed.
When you have enough information to answer the user, respond with:

Thought: [Your final reasoning]
Final Answer: [Your complete answer to the user in Vietnamese]

CONSTRAINTS:
- You can ONLY use the tools listed above. Do NOT invent tools.
- Always write Final Answer in Vietnamese.
- If a tool returns no data, try a different approach or give your best answer.
- Maximum {self.max_steps} steps allowed."""

    def run(self, user_input: str) -> str:
        """
        Vòng lặp ReAct chính.
        1. Gửi prompt cho LLM → nhận Thought + Action
        2. Parse Action → gọi Tool → nhận Observation
        3. Ghép Observation vào prompt → lặp lại
        4. Khi thấy "Final Answer" → dừng và trả kết quả
        """
        logger.log_event("AGENT_START", {
            "input": user_input,
            "model": self.llm.model_name,
            "max_steps": self.max_steps
        })

        self.trace = []  # Reset trace cho mỗi lần chạy
        current_prompt = f"User question: {user_input}"
        steps = 0
        total_tokens = 0

        while steps < self.max_steps:
            steps += 1

            # === Bước 1: Gọi LLM ===
            result = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            ai_response = result["content"]
            total_tokens += result["usage"].get("total_tokens", 0)

            # Ghi log
            logger.log_event("AGENT_STEP", {
                "step": steps,
                "response": ai_response[:300],
                "tokens": result["usage"],
                "latency_ms": result["latency_ms"]
            })

            # Ghi trace
            self.trace.append({
                "step": steps,
                "llm_output": ai_response,
                "latency_ms": result["latency_ms"],
                "tokens": result["usage"]
            })

            # === Bước 2: Kiểm tra Final Answer ===
            if "Final Answer:" in ai_response:
                final_answer = ai_response.split("Final Answer:")[-1].strip()

                logger.log_event("AGENT_END", {
                    "steps": steps,
                    "total_tokens": total_tokens,
                    "answer": final_answer[:200]
                })

                return final_answer

            # === Bước 3: Parse Action ===
            action_match = re.search(r'Action:\s*(\w+)\("?([^"]*?)"?\)', ai_response)

            if action_match:
                tool_name = action_match.group(1)
                tool_args = action_match.group(2).strip()

                # === Bước 4: Gọi Tool ===
                observation = self._execute_tool(tool_name, tool_args)

                # Ghi trace
                self.trace[-1]["action"] = f"{tool_name}(\"{tool_args}\")"
                self.trace[-1]["observation"] = observation

                logger.log_event("TOOL_CALL", {
                    "step": steps,
                    "tool": tool_name,
                    "args": tool_args,
                    "result": observation[:200]
                })

                # Ghép Observation vào prompt cho vòng lặp tiếp theo
                current_prompt += f"\n{ai_response}\nObservation: {observation}\n"

            else:
                # LLM không trả đúng format → ghi log lỗi
                logger.log_event("PARSE_ERROR", {
                    "step": steps,
                    "response": ai_response[:300]
                })
                self.trace[-1]["error"] = "Could not parse Action from response"

                # Thêm hướng dẫn để LLM sửa
                current_prompt += (
                    f"\n{ai_response}\n"
                    f"System: Your response was not in the correct format. "
                    f"Please use exactly: Action: tool_name(\"argument\") "
                    f"or Final Answer: your answer\n"
                )

        # Hết max_steps mà chưa có Final Answer
        logger.log_event("AGENT_TIMEOUT", {"steps": steps, "total_tokens": total_tokens})
        return "Xin lỗi, tôi không thể tìm được câu trả lời sau nhiều bước xử lý. Vui lòng thử hỏi lại cụ thể hơn."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """Tìm và gọi tool theo tên."""
        for tool in self.tools:
            if tool["name"] == tool_name:
                try:
                    return tool["function"](args)
                except Exception as e:
                    logger.log_event("TOOL_ERROR", {"tool": tool_name, "error": str(e)})
                    return f"Error calling {tool_name}: {str(e)}"

        return f"Error: Tool '{tool_name}' not found. Available tools: {[t['name'] for t in self.tools]}"

    def get_trace_report(self) -> str:
        """Xuất trace dạng đọc được cho báo cáo."""
        report = "=" * 60 + "\n"
        report += "📋 AGENT TRACE REPORT\n"
        report += "=" * 60 + "\n\n"

        for step in self.trace:
            report += f"--- Step {step['step']} ---\n"
            report += f"LLM Output:\n{step['llm_output']}\n"
            if "action" in step:
                report += f"\n🔧 Tool Called: {step['action']}\n"
                report += f"📥 Observation: {step['observation']}\n"
            if "error" in step:
                report += f"\n⚠️ Error: {step['error']}\n"
            report += f"⏱️ Latency: {step['latency_ms']}ms | Tokens: {step['tokens']}\n\n"

        return report
