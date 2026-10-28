# CHƯƠNG 5: FORM VÀ XỬ LÝ DỮ LIỆU NGƯỜI DÙNG

- **Môn học:** Phần mềm mã nguồn mở
- **Khoa:** Công nghệ Thông tin - Trường Đại học Khoa học, Đại học Huế
- **Phiên bản:** Hoàn thành Bài 1, Bài 2, Bài 3 (Buổi thực hành 7)
- **Giấy phép:** MIT License (SPDX-License-Identifier: MIT)

---

## 📱 Giới thiệu tổng quan
Dự án được xây dựng trên nền tảng **Python Flask** kết hợp **Bootstrap 5**, mô phỏng giao diện ứng dụng di động thông minh (Smartphone Mockup) đặt giữa không gian nền tối thiên hà với hiệu ứng các đốm sao liti lấp lánh.

Hệ thống tích hợp trọn vẹn 3 bài thực hành qua thanh Bottom Navigation:
1. **Bài 1 ★. Máy tính cơ bản:**
   - 4 phép tính cơ bản `+`, `-`, `*`, `/`.
   - Hỗ trợ số thập phân dấu phẩy (ví dụ: `2,5`).
   - Kiểm tra lỗi chia cho 0, phép toán không hợp lệ, giữ nguyên form sau submit.
2. **Bài 2 ★. Tính điểm học phần:**
   - Form 3 ô: Chuyên cần (10%), Giữa kỳ (30%), Cuối kỳ (60%).
   - Hàm kiểm tra dùng chung cho cả 3 ô (`validate_score`).
   - Quy tắc điểm liệt ($CK < 1.0$) và phân loại chữ ($A, B, C, D, F$).
3. **Bài 3 ★. Tính chỉ số BMI:**
   - Form Chiều cao (cm) và Cân nặng (kg).
   - Kiểm tra khoảng giá trị và cảnh báo người dùng nhập mét thay vì cm.
   - Phân loại thể trạng chuẩn người châu Á: Thiếu cân, Bình thường, Thừa cân, Béo phì.
   - Đổi màu khung kết quả (Xanh, Vàng, Đỏ) và tính khoảng cân nặng nên có (BMI $18.5 - 22.9$).

---

## 🚀 Hướng dẫn khởi chạy

1. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```
2. Khởi chạy ứng dụng:
   ```bash
   python main.py
   ```
3. Truy cập trình duyệt tại: `http://127.0.0.1:5000/`
