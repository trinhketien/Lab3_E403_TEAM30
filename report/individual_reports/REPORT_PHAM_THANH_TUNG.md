# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Phạm Thanh Tùng
- **Student ID**: 2A202600268
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

- **Modules Implemented**: `run_lab.py` (Benchmark) và `src/chatbot.py`.
  - Cấu hình Baseline Chatbot (Vanilla GPT-4o) để làm mốc xuất phát.
  - Lập trình hệ thống đo đạc hiệu chuẩn (Benchmarking) chạy tự động qua 5 chuỗi test-case điển hình từ dễ đén khó.
  - Trích xuất dữ liệu ranh giới: Số LLM Steps, Tổng Token ròng rã, và Thời gian ngâm Code (Latency in ms).

- **Code Highlights**:
```python
# Đo lường tổng Token tiêu hao của cả Agent và đống Loops
tokens_used = sum(step["tokens"]["total_tokens"] for step in agent.trace if "tokens" in step)
latency = (time.time() - start_time) * 1000  # ms
```
- **Documentation**: Benchmark của tôi bao bọc cả hàm chạy của Chatbot lẫn hàm `agent.run()`. Đây là thước đo pháp y cho thấy "Bộ não" ReAct hoạt động ngốn tài nguyên hệ thống khủng khiếp tới mức nào so với Baseline.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: Thống kê số lượng `total_tokens` của Agent trong bảng Log báo cáo bị sai lệch, khi chỉ báo có 300 Tokens (Nhỏ ngang bằng Chatbot), điều này vô lý vì ReAct vòng lặp rất nhiều đoạn văn.
- **Log Source**: Print log ở console báo: `Agent Tokens: 354, Chatbot Tokens: 320`.
- **Diagnosis**: Cách đo Token ban đầu của tôi bị lỗi: Tôi chỉ trích xuất tham số `usage.total_tokens` được trả về ở biến *Lần gọi API Cuối Cùng* (Final Answer). Nó đã chèn lấp xóa bỏ những Token bị nuốt vào ở quá trình LLM chạy step 1 và 2 trước đó.
- **Solution**: Tôi đã chèn hàm chạy vòng lặp Array lấy tổng mảng nội bộ `sum(...)` toàn bộ lượng token ở bên trong biến `agent.trace` của Backend. Đưa con số thật báo lên là 1,358 Tokens cho mỗi câu hỏi kép.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: Thay vì ép Baseline Chatbot trả lời nhúng 1 cục thẳng, The `Thought` block đã cưa nhỏ tư duy của GPT ra làm nhiều lớp. Điều này tương đương với hiệu ứng "Chain-of-Thought", gia tăng EQ giải quyết logic cực đỉnh mà chatbot không với tới.
2. **Reliability**: Sự cố "Over-Thinking". Nếu mình hỏi: "Cho lời khuyên học code?", Chatbot đáp lanh lẹ chuẩn bài. Agent thì kích hoạt tool "Search laptop" để kiếm Data. Vừa tốn 4 giây chạy tool vừa trả ra 1000 thẻ Token bị lạm pháp không đáng có cho 1 câu hỏi quá chung chung.
3. **Observation**: Khối Observation chứa rác nhiễu (Dư mô tả Rating/giá tiền râu ria) có thể kéo tuột tốc độ phân tích của AI ở vòng `Thought` kế tiếp. Việc tinh giảm Feedback ngắn gọn lại là cực kỳ cần thiết cho hiệu năng.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Ứng dụng quy chuẩn Automation CI/CD: Nếu Lõi Prompt có đổi mới trên nhánh Git, Github Actions lập tức tự `pytest` lại nguyên vẹn bộ 5 Test-cases này của tôi để giám sát coi Token Usage có bị lạm phát vượt trần 2000 token không.
- **Safety**: Bổ sung bộ đếm ngưỡng ngắt mạch vòng lặp `Fallback Token Limits`. Vượt 3000 Token tự ngắt luồng AI để chống cháy túi API Key thay vì chỉ dùng `Max_Steps = 5` cứng nhắc.
- **Performance**: Nhúng mô hình phân độ Model Routing (AI Router). Tạo 1 node AI rẻ tiền (Gemini Flash / Gpt-4o-mini) đứng chốt chặn đầu tiên. Nếu câu hỏi không cần đến Tool -> Routing qua thẳng Chatbot để lưu giữ tài nguyên và phản hồi cấp tốc.
