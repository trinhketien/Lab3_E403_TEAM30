# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Trịnh Kế Tiến
- **Student ID**: 2A202600500
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

### Key Role: Team Lead & Core Agent Developer

Trong tư cách là Trưởng nhóm & Kỹ sư thuật toán lõi (Core Agent Developer), tôi tập trung thiết kế và hoàn thiện logic trí tuệ tự động hóa (Agentic logic) thay vì làm các module tĩnh/dữ liệu. Các đóng góp cụ thể của tôi bao gồm:

1. **Vòng lặp ReAct (`src/agent/agent.py`)** — Trái tim của hệ thống:
   - Thiết kế Prompt Hệ Thống (System Prompt) linh hoạt với 5 phần cấu trúc (Identity, Capabilities, Instructions, Constraints, Output Format).
   - Implement vòng lặp ReAct cốt lõi: Liên tục xoay vòng `generate` → `parse` → `execute tool` → `append observation` cho đến khi có Final Answer (giới hạn max_steps).
   
2. **Cơ chế Tự Phục Hồi (Self-Healing) & Error Handling**:
   - Cài đặt Regex cắt chuỗi thông minh bắt và phân tách Thought/Action của LLM.
   - Thêm tính năng **Self-Healing**: Khi LLM trả sai định dạng (quên ngoặc, dư chữ), code thay vì sập (`v1`) sẽ tự động đánh chặn và gửi chỉ thị `System: Your response was not in the correct format...` để ép LLM xử lý chuẩn hóa lại format ngay trong quá trình runtime.

3. **Kiến trúc Versioning & Trace Logging**:
   - Xây dựng thuộc tính `self.trace` và hàm `get_trace_report()` để tracking toàn bộ suy nghĩ qua từng Step phục vụ cho việc visualize lên Giao diện Web.
   - Setup phiên bản đối xứng `agent_v1.py` (cố tình để lỗi loop) làm cơ sở cho thành viên khác phân tích RCA.

### Code Highlights

```python
# Phần parse Action — dùng Regex để tách tool_name và arguments
action_match = re.search(r'Action:\s*(\w+)\("?([^"]*?)"?\)', ai_response)
if action_match:
    tool_name = action_match.group(1)
    tool_args = action_match.group(2).strip()
    observation = self._execute_tool(tool_name, tool_args)
```

```python
# Error handling khi parse fail — không crash, mà hướng dẫn LLM sửa
else:
    current_prompt += (
        f"\nSystem: Your response was not in the correct format. "
        f"Please use exactly: Action: tool_name(\"argument\")"
    )
```

### How My Code Interacts with the ReAct Loop

Code tôi viết chính là **vòng lặp ReAct cốt lõi**:
1. `run()` gọi `self.llm.generate()` (dùng Provider có sẵn) → nhận response
2. Parse response bằng regex để tách Thought/Action/Final Answer
3. Nếu có Action → gọi `_execute_tool()` → lấy Observation → ghép vào prompt
4. Nếu có Final Answer → trả kết quả
5. Nếu parse fail → gửi hướng dẫn sửa format cho LLM

---

## II. Debugging Case Study (10 Points)

### Problem Description
Khi chạy test case "Nên mua laptop hãng nào cho sinh viên?", Agent gọi `search_products("laptop")` dù câu hỏi chỉ cần lời khuyên chung — **Agent tốn 1,358 tokens** trong khi Chatbot chỉ tốn 254 tokens.

### Log Source
```json
{"timestamp": "2026-04-06T07:44:14", "event": "AGENT_STEP", "data": {"step": 1, "response": "Thought: Để tư vấn laptop cho sinh viên, tôi cần tìm các sản phẩm laptop phù hợp.\nAction: search_products(\"laptop\")", "tokens": {"total_tokens": 354}}}
{"timestamp": "2026-04-06T07:44:17", "event": "TOOL_CALL", "data": {"step": 1, "tool": "search_products", "args": "laptop"}}
```

### Diagnosis
Agent được thiết kế để **luôn cố gắng dùng tools** vì system prompt hướng dẫn "You have access to tools". Với câu hỏi đơn giản, Agent vẫn gọi tool dù không cần thiết → tốn tokens + tốn thời gian.

**Root cause**: System prompt thiếu hướng dẫn "Nếu câu hỏi chỉ cần kiến thức chung, không cần gọi tool, hãy trả Final Answer ngay".

### Solution
Thêm vào system prompt (v2):
```
- If the question only requires general knowledge and does NOT need specific product data, 
  go directly to Final Answer without calling any tool.
```

Kết quả: Agent v2 phân biệt được câu hỏi chung vs câu cần tool, giảm unnecessary tool calls.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

### 1. Reasoning — Thought block giúp Agent thế nào?

Block `Thought` ép Agent phải **suy nghĩ trước khi hành động**. Ví dụ Test Case 3 ("Tìm laptop dưới 16 triệu rồi so sánh"):

- **Chatbot**: Trả lời ngay → bịa thông số, không chính xác
- **Agent Thought 1**: "Cần tìm danh sách laptop trước" → gọi `search_products`
- **Agent Thought 2**: "Trong kết quả, Acer Aspire 5 và ASUS VivoBook 15 có rating cao nhất" → gọi `compare_specs`
- **Agent Thought 3**: "Đã có đủ data để tư vấn" → Final Answer với số liệu cụ thể

→ Thought block tạo ra **chuỗi suy luận rõ ràng**, giúp dễ debug và verify.

### 2. Reliability — Khi nào Agent tệ hơn Chatbot?

Agent tệ hơn khi:
- **Câu hỏi đơn giản** (Test 1, 2): Agent tốn gấp 3-5x tokens vì vẫn cố gọi tool
- **Latency cao hơn**: Agent cần 2-3 vòng lặp, mỗi vòng ~1-2 giây, tổng thời gian dài hơn
- **Chi phí cao hơn**: Gấp 3.5x token = gấp 3.5x tiền

→ **Kết luận**: Không phải mọi bài toán đều cần Agent. Dùng Agentic Fit score để đánh giá trước.

### 3. Observation — Feedback từ environment ảnh hưởng thế nào?

Observation (kết quả tool trả về) **thay đổi hướng suy luận** của Agent:
- Test 3: Observation từ `search_products` chứa 5 sản phẩm → Agent tự chọn 2 cái tốt nhất dựa trên rating → gọi `compare_specs` cho đúng 2 cái đó
- Test 5 (Edge case): Observation trả "Không tìm thấy" → Agent **không lặp vô ích**, thay vào đó trả Final Answer bằng kiến thức có sẵn

→ Observation là **feedback loop** giúp Agent **thích ứng** (adaptive) thay vì cứng nhắc.

---

## IV. Future Improvements (5 Points)

### Scalability
- **Async tool calls**: Gọi nhiều tools song song (ví dụ: tìm sản phẩm + check review cùng lúc) bằng `asyncio` để giảm tổng latency
- **Caching**: Cache kết quả tool đã gọi → không gọi lại nếu cùng input

### Safety
- **Supervisor Agent**: Thêm 1 LLM thứ 2 kiểm tra output của Agent trước khi trả cho user (audit layer)
- **Input sanitization**: Validate và filter input trước khi truyền vào tools để tránh injection

### Performance
- **Vector Database**: Khi có catalog hàng nghìn sản phẩm, dùng embedding + vector search thay vì mock data
- **Multi-Agent System**: Tách thành nhiều agent chuyên biệt (SearchAgent, CompareAgent, ReviewAgent) phối hợp qua orchestrator
- **RAG Integration**: Kết hợp Retrieval-Augmented Generation để agent truy xuất tài liệu sản phẩm thực

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
