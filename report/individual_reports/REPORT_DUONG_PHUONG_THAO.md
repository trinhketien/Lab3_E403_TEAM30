# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Dương Phương Thảo
- **Student ID**: 2A202600049
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

- **Modules Implemented**: `report/` và Phân tích `logs/`.
  - Phụ trách luồng kiểm định chất lượng (QA/RCA), quản lý mảng File Hệ thống và Nhật ký sinh mạng hệ thống (JSON Log Traces).
  - Biên dịch toàn bộ mô hình ReAct ra ngôn ngữ Sơ đồ luồng (Flowchart Diagram) phục vụ báo cáo.
  - Phối hợp lắp ghép 4 mảnh ghép độc lập của các Dev khác thành bản Tổng Cáo Bạch Group Project hoàn thiện.

- **Code Highlights**:
```json
// Quản trị luồng Trace ẩn sâu của log (Phát hiện lỗi Edge Case)
{"event": "TOOL_CALL", "data": {"tool": "search_products", "args": "washing machine", "result": "Không tìm thấy sản phẩm"}}
{"event": "AGENT_STEP", "data": {"response": "Thought: Dữ liệu không có. Trả về khuyên tổng quát"}}
```
- **Documentation**: Mảng System Log và Documentation tôi làm là công cụ dịch thuật giữa "Luồng code mù mờ" của Developer thành hình hài rõ ràng định tính cho Giảng viên/Stakeholder có thể chấm điểm được.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: Lần khảo sát code Core `agent_v1.py` đời cổ, Agent bị rớt vào vòng xoáy Infinite Loop (Vòng lặp Vô cực). Chạy liên thanh 60s trên Terminal không nhả câu trả lời mồi nào, khiến hệ thống báo Timeout Error.
- **Log Source**: `{"event": "PARSE_ERROR", "Action Not Found in output"}` xen lẫn hàng chục `{"event": "AGENT_STEP"}` trống lỗi mờ.
- **Diagnosis**: Kỹ thuật cắt Regex ban đầu ở phần Parse cực dính. LLM GPT-4o lúc sinh câu bị xót dấu chấm và ngoặc kép: `Action: compare_specs asus`. Code Regex bó tay không bóc được lõi -> Trục xuất Tool, LLM không nhận được Data Observation nên tự xoay tiếp rồi bị điên.
- **Solution**: Team tiến hành cơ chế (Self-Healing). Tôi gửi rà soát nguyên nhân về rễ để Tiến chèn 1 dòng lệnh Error Context `System: Your response was out of bounds` gửi thẳng đập ngược vào mồm LLM. Agent ngay lập tức xin lỗi và sửa ngữ pháp ở lượt lặp số 2. Lỗi Crash 100% biến mất.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: Tư duy khối lượng (Thought process) thay đổi cục diện ngành. Việc nhìn log thấy LLM tự vấn "Câu này chưa đủ data, phải so sánh tiếp với hãng khác" mang đến sự kinh ngạc tận cùng. Agent không phải cái gõ chữ, nó là cỗ máy giải quyết Vấn đề.
2. **Reliability**: Sự tệ hại của Agent bùng phát ở mốc giới hạn Data. Nếu Tool API chết, Chatbot vẫn dùng kiến thức mạng có sẵn vớt lại thể diện. Agent phụ thuộc Tool nên đôi khi bị động, rơi vào trạng thái báo lỗi Server Internal do Tool rụng mạng.
3. **Observation**: Feedback của hệ thống khi tôi thử nhét chữ "Máy Giặt". Observation trả về `Not Found`, ngay lập tức định hình Block Thought tiếp theo ngưng truy cập Database và nhảy sang trạng thái kết luận chay -> Tránh mắc kẹt vòng lặp. Feedback là ngọn hải đăng cho agent đi.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Tích hợp Centralized ELK Stack (Elasticsearch, Logstash, Kibana). Từ bỏ việc ghi JSON bằng mảng `.log` thủ công ra File Text, và đưa tất cả Log vào Dashboard đồ họa hiển thị trực quan tỷ lệ sập lỗi hệ thống hàng ngày.
- **Safety**: Xây dựng mỏ neo System Audit: Bất cứ lúc nào Agent định gọi 1 Tool có yếu tố "Mua sắm / Thanh Toán", quy chuẩn ép buộc luồng LLM phải rơi vào trạng thái Pause chờ Con người nhấp (Approve) trên Web để ngăn AI quẹt thẻ tín dụng bừa bãi.
- **Performance**: Phân tách luồng Micro-services hệ thống, cho Tools nằm độc lập ở Server Backend B; Agent nằm độc lập ở Server A. Rút nhẹ gánh nặng bộ nhớ RAM máy tính.
