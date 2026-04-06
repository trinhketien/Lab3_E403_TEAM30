"""
ReAct Agent v1 — Phiên bản ĐẦU TIÊN, có các lỗi đã biết.
File này lưu lại để so sánh với v2 (agent.py).

Các lỗi của v1:
1. System prompt quá đơn giản, thiếu constraints
2. Không xử lý khi parse Action fail → crash
3. Không xử lý khi tool trả "không có data"
4. Không có trace logging
"""
import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger


class ReActAgentV1:
    """
    Agent v1 — Phiên bản cơ bản, có nhiều hạn chế.
    """

    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps

    def get_system_prompt(self) -> str:
        """
        v1 System Prompt — ĐƠN GIẢN, thiếu nhiều hướng dẫn.
        Vấn đề:
        - Không có constraints (ràng buộc)
        - Không hướng dẫn xử lý khi tool fail
        - Không yêu cầu trả lời bằng tiếng Việt
        """
        tool_descriptions = "\n".join(
            [f"- {t['name']}: {t['description']}" for t in self.tools]
        )
        return f"""You are an assistant. You have tools:
{tool_descriptions}

Use this format:
Thought: your reasoning
Action: tool_name(arguments)
Observation: result
Final Answer: your answer"""

    def run(self, user_input: str) -> str:
        """
        v1 ReAct Loop — Thiếu error handling.
        Vấn đề:
        - Không xử lý parse error → dễ lặp vô hạn
        - Không ghi trace
        - Không log chi tiết
        """
        logger.log_event("AGENT_V1_START", {"input": user_input})

        current_prompt = user_input
        steps = 0

        while steps < self.max_steps:
            steps += 1

            result = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            ai_response = result["content"]

            # Kiểm tra Final Answer
            if "Final Answer:" in ai_response:
                final_answer = ai_response.split("Final Answer:")[-1].strip()
                logger.log_event("AGENT_V1_END", {"steps": steps})
                return final_answer

            # Parse Action — KHÔNG có error handling
            action_match = re.search(r'Action:\s*(\w+)\((.*?)\)', ai_response)

            if action_match:
                tool_name = action_match.group(1)
                tool_args = action_match.group(2).strip().strip('"')
                observation = self._execute_tool(tool_name, tool_args)
                current_prompt += f"\n{ai_response}\nObservation: {observation}\n"
            # BUG: Nếu không parse được Action → không làm gì cả
            # → Agent tiếp tục loop với cùng prompt → LẶP VÔ HẠN

            # Không có: gửi lại hướng dẫn format cho LLM
            # Không có: ghi trace
            # Không có: log PARSE_ERROR

        logger.log_event("AGENT_V1_TIMEOUT", {"steps": steps})
        return "Agent could not find an answer."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """v1: Không có try/except → crash nếu tool lỗi."""
        for tool in self.tools:
            if tool["name"] == tool_name:
                return tool["function"](args)  # Không có try/except!
        return f"Tool {tool_name} not found."
