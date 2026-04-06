# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Mai Phi Hiếu
- **Student ID**: 2A202600126
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

- **Modules Implemented**: `src/tools/shopping_tools.py`
  - Thiết kế Mock Database trải dài qua 6 danh mục (Laptop, Phone, Tablet, Headphone, Smartwatch, Camera) với hơn 25 sản phẩm.
  - Viết 3 Custom Tools (`search_products`, `compare_specs`, `check_reviews`) cho hệ thống.
  - Tối ưu hóa Tool Description để ép LLM truyền đúng chuẩn tham số.

- **Code Highlights**:
```python
{
    "name": "compare_specs",
    "description": "Compare specifications of two products side by side. Input: two product names separated by space e.g. 'acer aspire asus'. Output: comparison table.",
    "function": compare_specs
}
```
- **Documentation**: Mảng Tools do tôi viết đóng vai trò là "Môi trường thực tế" (Environment). Khi vòng lặp ReAct của bạn Tiến quăng tham số xuống, hàm của tôi chộp lấy và trả về Data thông số thật (Observation) cho AI đọc.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: LLM liên tục truyền sai tham số cho hàm `compare_specs`. Nó truyền mảng JSON `["acer", "asus"]` thay vì String, làm code báo `TypeError`.
- **Log Source**: `{"event": "TOOL_CALL", "args": "[\"acer\", \"asus\"]"}`
- **Diagnosis**: Do phần `description` ban đầu của tool quá ngắn gọn (`"Compare two products"`), LLM không được mớm luật nên tự bịa cấu trúc data truyền vào.
- **Solution**: Tôi viết lại Description cực kỳ quy chuẩn: `"Input: two product names separated by space (string)"`. Sau đó LLM tự hiểu và nạp tham số đúng 100%.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: Khối `Thought` giúp AI thoát khỏi việc suy đoán bừa. Khi có Tools của tôi, Agent dựa vào Thought để lên kế hoạch "Cần gọi hàm search trước khi trả lời" thay vì phun bừa kiến thức cũ kỹ giống Chatbot.
2. **Reliability**: Agent kém Chatbot khi bị ép trả lời những câu lý thuyết rỗng. Lúc đó, AI cứ loay hoay vào giỏ Data của tôi tìm kiếm khiến nó bị timeout, trong khi Chatbot trả lời xong từ lâu.
3. **Observation**: Feedback trả về rỗng (VD: "Không tìm thấy máy giặt") ngay lập tức khiến Agent tự reset lại Thought trong bước tiếp theo, chuyển hướng xin lỗi người dùng thay vì đâm đầu gọi lại Tool.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Thay vì mock data dict trong code, tôi sẽ dựng Docker chứa CSDL PostgreSQL và dùng Vector DB (Milvus) để hỗ trợ tìm kiếm mờ (Fuzzy Search) khi truyền hàng ngàn sản phẩm.
- **Safety**: Viết thêm hàm Pydantic `BaseModel` Validation cắm đè lên các Tool để kiểm duyệt độc hại từng parameter trước khi chọt xuống Database.
- **Performance**: Xây dựng cơ chế Async (Bất đồng bộ) cho tất cả các Tool để có thể gọi cả hàm Search và Report cùng lúc rút ngắn độ trễ từ 5 giây xuống 2 giây.
