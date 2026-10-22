# Shopee Smart Assistant — bản demo

Đây là chatbot mẫu phục vụ bài tập học thuật. **Không phải sản phẩm chính thức của Shopee**. Dữ liệu sản phẩm, review và doanh số đều là dữ liệu giả lập.

## Chức năng
- Tìm sản phẩm theo danh mục và ngân sách
- Tra cứu thông tin sản phẩm
- Truy xuất review và phân tích cảm xúc bằng bộ từ khóa đơn giản
- Dự báo nhu cầu tuần tiếp theo bằng trung bình 3 tuần gần nhất
- Xử lý câu hỏi ngoài phạm vi
- Hiển thị các bảng dữ liệu mẫu

## Cách chạy trên Windows
1. Cài Python 3.10 trở lên từ https://www.python.org/downloads/
2. Giải nén thư mục dự án.
3. Mở Command Prompt/Terminal tại thư mục `shopee_smart_assistant`.
4. (Khuyến nghị) Tạo môi trường ảo:
   `python -m venv .venv`
5. Kích hoạt môi trường ảo:
   - CMD: `.venv\\Scripts\\activate`
   - PowerShell: `.venv\\Scripts\\Activate.ps1`
6. Cài thư viện:
   `pip install -r requirements.txt`
7. Chạy chatbot:
   `streamlit run app.py`
8. Trình duyệt sẽ mở giao diện; nếu không, truy cập địa chỉ localhost mà terminal hiển thị.

## Câu hỏi thử
- `Tìm tai nghe dưới 500 nghìn`
- `Thông tin Tai nghe Bluetooth A`
- `Review Tai nghe Bluetooth A`
- `Dự báo nhu cầu Tai nghe Bluetooth A tuần sau`
- `Ngày mai Hà Nội có mưa không?`

## Giới hạn cần ghi trong báo cáo
- Dữ liệu hoàn toàn giả lập, không phải dữ liệu Shopee.
- Sentiment dựa trên từ khóa, chưa phải mô hình NLP được huấn luyện; có thể sai với phủ định, mỉa mai hoặc câu có cả khen và chê.
- Forecast dùng trung bình 3 tuần gần nhất, là mô hình baseline đơn giản, không chứng minh hiệu quả dự báo thực tế.
- Chatbot chưa kết nối API, đơn hàng, tài khoản, giá hoặc tồn kho thật của Shopee.

## Cấu trúc
- `app.py`: ứng dụng chatbot
- `data/products.csv`: sản phẩm
- `data/reviews.csv`: đánh giá
- `data/weekly_sales.csv`: doanh số giả lập theo tuần
- `test_cases.csv`: bộ kiểm thử ban đầu
