# Bài tập Chương 4: Ứng dụng Cà phê Sông Hương (Flask & Jinja2 Template)

## 1. Giới thiệu
Ứng dụng web hiển thị thông tin quán cà phê, thời gian hoạt động, tự động kiểm tra trạng thái mở/đóng cửa và hiển thị danh sách khuyến mãi sử dụng Flask và Jinja2 template.

## 2. Cấu trúc thư mục
```text
Chuong4/
├── .gitignore
├── .venv/
├── __pycache__/
├── cafe.py
├── requirements.txt
├── README.md
└── templates/
    └── index.html
```

## 3. Hướng dẫn khởi chạy
1. Kích hoạt môi trường ảo:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
2. Cài đặt thư viện phụ thuộc:
   ```powershell
   pip install -r requirements.txt
   ```
3. Khởi chạy ứng dụng:
   ```powershell
   python cafe.py
   ```
4. Truy cập trình duyệt tại: `http://127.0.0.1:5000/`

## 4. Kiểm thử với tham số giờ (?gio=...)
- Xem trạng thái mở cửa: `http://127.0.0.1:5000/?gio=10`
- Xem trạng thái đóng cửa: `http://127.0.0.1:5000/?gio=23`
