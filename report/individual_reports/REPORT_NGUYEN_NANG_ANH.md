# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Năng Anh
- **Student ID**: 2A202600184
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

- **Modules Implemented**: `web_demo.py` và luồng UI.
  - Sử dụng Flask framework thiết kế Web UI màn hình đôi (Side-by-side) so sánh trực tiếp tốc độ và câu trả lời của Chatbot vs Agent.
  - Bóc tách mảng `self.trace` nội bộ để vẽ lên màn hình các khối Thought -> Action -> Observation trực quan dạng bong bóng mờ (X-ray UI).

- **Code Highlights**:
```python
# Bóc lấy mảng lịch sử tư duy truyền xuống file HTML Template
trace = agent.get_trace_report() 
return jsonify({
    "chatbot": chatbot_answer,
    "agent": agent_answer,
    "trace": trace  # Dữ liệu cốt lõi render Thought Block
})
```
- **Documentation**: Mảng Web của tôi lắng nghe API trả về từ lõi ReAct (`agent.run(query)`). Tôi phân rã object JSON cuối cùng ra 3 vùng: Nội dung hiển thị, tốc độ phản hồi (Latency), và vệt sáng tư duy (Trace) để người dùng giám sát.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: Khi User nhập câu hỏi bắt AI chạy 4 vòng lặp (vừa tìm, vừa so sánh), trình duyệt Web UI bị xoay tròn Loading mãi mãi rồi ngắt kết nối (Timeout Error).
- **Log Source**: Console hiển thị `504 Gateway Timeout` do mất quá 15s chờ OpenAI API.
- **Diagnosis**: Flask hoạt động theo chuẩn đồng bộ (Synchronous). Vòng lặp Agent bị blocking quá trình phản hồi HTTP, khiến Web UI tịt ngòi 100% đến khi kết thúc hẳn toàn bộ loop.
- **Solution**: Lập trình thêm cơ chế Loading Animators phía Client-side CSS, chặn (Disable) mọi thao tác nhấp chuột khi API đang kẹt, giúp user nhận biết hệ thống "Vẫn đang tư duy" chứ không sập. Cứu rỗi UX.

---

