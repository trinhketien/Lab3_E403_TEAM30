# Group Report: Lab 3 - Chatbot vs ReAct Agent

- **Team Name**: AI20K-Nhóm 30
- **Team Members**: Trịnh Kế Tiến (2A202600500), Mai Phi Hiếu(2A202600126), Nguyễn Năng Anh(2A202600184), Phạm Thanh Tùng(2A202600268), Dương Phương Thảo(2A202600049) 
- **Date**: 2026-04-06

---

## 1. Executive Summary

Nhóm đã xây dựng hệ thống **Trợ Lý Mua Sắm Thông Minh** để so sánh Chatbot baseline với ReAct Agent. Kết quả cho thấy Agent vượt trội rõ rệt trong các tác vụ multi-step (tìm kiếm + so sánh + review), trong khi Chatbot hiệu quả hơn cho câu hỏi đơn giản.

- **Success Rate**: Agent trả lời chính xác 5/5 test cases (100%), trong đó 3 cases có dữ liệu thật từ tools
- **Key Outcome**: Agent giải quyết được bài toán multi-step mà Chatbot không thể: tìm sản phẩm theo budget → so sánh thông số → check review → đưa ra tư vấn có căn cứ

### 1.1 Team Contributions (Phân chia công việc)

Dự án được phân chia thành 5 module chuyên biệt, tương ứng với 5 thành viên trong nhóm để tối ưu hóa hiệu suất và dễ dàng triển khai Github workflow:

1. **Trịnh Kế Tiến (Team Lead & Core Agent)**: Chịu trách nhiệm thiết kế thuật toán cốt lõi cho ReAct Agent. Viết System Prompt, vòng lặp suy luận Thought-Action-Observation và cơ chế phát hiện lỗi/tự sửa cấu trúc (Self-Healing). *(Phụ trách: `src/agent/agent.py`)*
2. **Mai Phi Hiếu (Tooling & Data Engineer)**: Thiết kế 3 Tools hệ thống và cung cấp cơ sở dữ liệu giả lập (Mock data) đa dạng (Laptop, Điện thoại, Máy ảnh, Tai nghe, Smartwatch...) làm dữ liệu nền tảng cho Agent truy xuất. *(Phụ trách: `src/tools/shopping_tools.py`)*
3. **Nguyễn Năng Anh (Frontend & System Dev)**: Thiết kế giao diện Web Demo (Flask). Tích hợp bot lên nền tảng website trực quan, viết module bóc tách Trace để hiển thị rõ ràng luồng suy nghĩ của AI trên trình duyệt. *(Phụ trách: `web_demo.py` & `demo.py`)*
4. **Phạm Thanh Tùng (QA/Evaluation Engineer)**: Thiết lập môi trường thử nghiệm tự động. Viết kịch bản `run_lab.py` để đo lường các chỉ số Benchmark (Token usage, Latency, Số vòng lặp) giữa Chatbot và Agent. *(Phụ trách: `run_lab.py` & `src/chatbot.py`)*
5. **Dương Phương Thảo (Technical Writer & RCA Analyst)**: Phân tích file JSON Log để tìm Nguyên nhân gốc rễ (RCA) hệ thống. Trực tiếp phát hiện lỗi lặp vô hạn ở v1 và làm báo cáo tổng hợp, thiết kế sơ đồ Flowchart và tài liệu tham khảo. *(Phụ trách: `report/`, `logs/`)*

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation

```
User Input
    │
    ▼
┌──────────────────┐
│  System Prompt    │ ← Identity + Tools + Format + Constraints
│  + User Query     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐       ┌───────────────────┐
│  LLM Generate    │       │  AVAILABLE TOOLS   │
│  (GPT-4o)        │       │                   │
│                  │       │ • search_products  │
│  Output:         │       │ • compare_specs    │
│  Thought + Action│       │ • check_reviews    │
└────────┬─────────┘       └───────────────────┘
         │
    ┌────┴────┐
    │ Parse   │ ← Regex: r'Action:\s*(\w+)\("?([^"]*?)"?\)'
    │Response │
    └────┬────┘
         │
   ┌─────┴──────┐───────────┐
   │            │           │
   ▼            ▼           ▼
Final Answer  Action    Parse Error
   │          found?        │
   │            │           │ (v2 only)
   │      Execute Tool  Send format
   │            │       correction
   │       Observation      │
   │            │           │
   │         Append <───────┘
   │       to Prompt 
   │            │
   │            └──→ Back to LLM (max 5 loops)
   ▼
Return Answer to User
```

### 2.2 Tool Definitions (Inventory)

| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `search_products` | `string` (keyword: "laptop", "phone", "tablet") | Tìm sản phẩm theo danh mục, trả về giá, thông số, rating |
| `compare_specs` | `string` (2 tên sản phẩm) | So sánh thông số kỹ thuật side-by-side |
| `check_reviews` | `string` (tên sản phẩm) | Tra đánh giá: rating, ưu/nhược, kết luận |

### 2.3 LLM Providers Used
- **Primary**: GPT-4o (OpenAI)

---

## 3. Agent v1 → v2 Evolution

### 3.1 Các lỗi của Agent v1 (`agent_v1.py`)

| Lỗi | Mô tả | Hậu quả |
| :--- | :--- | :--- |
| **System prompt đơn giản** | Không có constraints, không yêu cầu trả lời tiếng Việt | Agent trả lời tiếng Anh, gọi tool không cần thiết |
| **Không xử lý parse error** | Khi LLM trả sai format, code không làm gì | Agent lặp vô hạn với cùng prompt |
| **Không xử lý tool fail** | Không có try/except khi gọi tool | Code crash khi tool báo lỗi |
| **Không ghi trace** | Không lưu quá trình suy luận | Không thể debug, không có data cho báo cáo |

### 3.2 Cải tiến trong Agent v2 (`agent.py`)

| Vấn đề v1 | Fix trong v2 | Code |
| :--- | :--- | :--- |
| Prompt đơn giản | Thêm 5 phần: Identity, Capabilities, Instructions, **Constraints**, Output Format | `get_system_prompt()` |
| Parse error → loop | Phát hiện parse fail → gửi hướng dẫn format lại cho LLM | `"System: Your response was not in correct format..."` |
| Tool crash | Bọc `try/except` trong `_execute_tool()` | `except Exception as e: return f"Error: {e}"` |
| Không có trace | Thêm `self.trace[]` + `get_trace_report()` | Mỗi step ghi: LLM output, action, observation, latency |

### 3.3 So sánh System Prompt v1 vs v2

**v1 (đơn giản, thiếu sót):**
```
You are an assistant. You have tools:
- search_products: ...
Use this format:
Thought: your reasoning
Action: tool_name(arguments)
Final Answer: your answer
```

**v2 (đầy đủ, có constraints):**
```
You are a Smart Shopping Assistant. You help users find and compare products.

AVAILABLE TOOLS: ...

INSTRUCTIONS:
You MUST follow this exact format...

CONSTRAINTS:
- You can ONLY use the tools listed above. Do NOT invent tools.
- Always write Final Answer in Vietnamese.
- If a tool returns no data, try a different approach or give your best answer.
- Maximum 5 steps allowed.
```

**Kết quả cải tiến:**
- v2 trả lời tiếng Việt (v1 trả tiếng Anh)
- v2 xử lý edge case "máy giặt" gracefully (v1 crash hoặc loop)
- v2 có trace đầy đủ để debug (v1 không có gì)

---

## 4. Tool Design Evolution

### v1 Tool Description (quá đơn giản):
```
search_products: Search for products
compare_specs: Compare two products
check_reviews: Get reviews
```
→ **Vấn đề**: LLM không biết input format → gọi tool sai arguments → Observation lỗi

### v2 Tool Description (rõ ràng, chi tiết):
```
search_products: Search for products by category keyword.
  Input: a keyword like 'laptop', 'phone', or 'tablet' (string).
  Output: list of products with name, price, specs, and rating.

compare_specs: Compare specifications of two products side by side.
  Input: two product names separated by space (string).
  Output: comparison table.

check_reviews: Check user reviews and ratings for a specific product.
  Input: product name (string).
  Output: rating, pros, cons, and verdict.
```
→ **Kết quả**: Agent v2 gọi đúng tool, đúng arguments 100% test cases.

---

## 5. Telemetry & Performance Dashboard

| Metric | Chatbot | Agent v2 |
| :--- | :--- | :--- |
| **Avg Tokens/Task** | 349 tokens | 1,232 tokens |
| **Total Tokens (5 tests)** | 1,745 | 6,158 |
| **Avg Latency** | ~3,300ms | ~3,400ms |
| **Avg Steps** | 1 | 2.0 |
| **Cost Estimate** | ~$0.017 | ~$0.062 |

---

## 6. Root Cause Analysis (RCA) - Failure Traces

### Case 1: Parse Error (v1)
- **Input**: "Tìm laptop dưới 16 triệu rồi so sánh 2 cái tốt nhất"
- **v1 Behavior**: LLM trả `Action: compare_specs("Acer Aspire 5", "ASUS VivoBook 15")` — regex v1 không parse được dấu phẩy → không gọi được tool → loop vô hạn cho đến max_steps
- **v2 Fix**: Regex mở rộng + gửi format correction → LLM tự sửa lại format

### Case 2: Edge Case — Tool không có data (v1 vs v2)
- **Input**: "Tìm máy giặt"
- **v1**: `search_products` trả "Không tìm thấy" → v1 không biết xử lý → tiếp tục gọi lại tool → loop
- **v2**: Nhận Observation lỗi → Thought: "Không có data" → trả Final Answer bằng kiến thức có sẵn (graceful degradation)

---

## 7. Ablation Studies & Experiments

### Chatbot vs Agent trên 5 test cases

| # | Case | Chatbot | Agent v2 | Winner |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Kiến thức chung | ✅ Đúng (370 tokens) | ✅ Đúng nhưng dư (670 tokens) | **Chatbot** |
| 2 | Lời khuyên | ✅ Đúng (254 tokens) | ✅ Nhưng gọi tool dư (1,358 tokens) | **Chatbot** |
| 3 | Tìm + So sánh | ⚠️ Bịa thông số | ✅ Data thật, so sánh chính xác | **Agent** |
| 4 | Tìm + Review | ⚠️ Gợi ý chung | ✅ Review cụ thể: rating, pros/cons | **Agent** |
| 5 | Sản phẩm không có | ⚠️ Bịa sản phẩm | ✅ Thừa nhận không có data | **Agent** |

---

## 8. Production Readiness Review

- **Security**: Tool chỉ nhận string input đơn giản, không có rủi ro injection. Trong production cần thêm input sanitization.
- **Guardrails**: `max_steps = 5` ngăn loop vô hạn. Error handling cho parse failure + tool error.
- **Scaling**:
  - Kết nối API thật (Tiki, Shopee, Lazada) thay mock data
  - RAG + Vector Database cho catalog lớn
  - Multi-agent system: SearchAgent + CompareAgent + ReviewAgent
  - Supervisor Agent để audit quyết định

---

> [!NOTE]
> Submit this report by renaming it to `GROUP_REPORT_[TEAM_NAME].md` and placing it in this folder.
