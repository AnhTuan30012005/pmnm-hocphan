# BÀI TẬP KIỂM TRA (100 ĐIỂM): HỆ THỐNG QUẢN LÝ THƯ VIỆN & SÁCH

- **Học phần:** Phần mềm mã nguồn mở
- **Giảng viên:** Thầy Nguyễn Dũng (ndung@husc.edu.vn)
- **Khoa:** Công nghệ Thông tin - Trường Đại học Khoa học, Đại học Huế
- **Sinh viên thực hiện:** Nguyễn Anh Tuấn
- **Mã sinh viên:** `23T1080089`
- **Email:** `23T1080089@husc.edu.vn`
- **Nền tảng:** Python 3.11, Flask 3.1, Flask-SQLAlchemy 3.1 (chuẩn SQLAlchemy 2.0), SQLite, Bootstrap 5, Chart.js

---

## 1. Yêu cầu đề bài & Nội dung đã hoàn thành (100% 4/4)

### 1.1. CRUD Danh mục Sách (Category)
- [x] **Danh sách danh mục (`/categories`):** Bảng hiển thị danh mục, mô tả, số lượng sách thuộc danh mục, ngày tạo và tìm kiếm nhanh.
- [x] **Thêm danh mục mới (`/categories/add`):** Form nhập Tên danh mục, Mô tả. Tự động kiểm tra lỗi bỏ trống và lỗi trùng lặp (`unique=True`).
- [x] **Chỉnh sửa danh mục (`/categories/edit/<id>`):** Cập nhật tên và mô tả danh mục.
- [x] **Xóa danh mục (`/categories/delete/<id>`):** Xóa danh mục kèm cơ chế liên kết dữ liệu an toàn (`cascade="all, delete-orphan"`).

### 1.2. CRUD Sách theo danh mục (Book)
- [x] **Danh sách sách (`/books`):**
  - Lọc theo danh mục được chọn (`?category_id=...`).
  - Thanh nhãn lọc nhanh (Pills) theo từng thể loại.
  - Ô tìm kiếm linh hoạt theo Tên sách hoặc Tác giả (`?q=...`).
  - Lọc theo trạng thái còn hàng / hết hàng (`?status=...`).
  - Sắp xếp theo giá (tăng/giảm dần) hoặc năm xuất bản (`?sort=...`).
- [x] **Xem chi tiết sách (`/books/<id>`):** Trang thông tin toàn diện về sách, thẻ phân loại danh mục, tác giả, giá tiền, số lượng kho, thời gian lưu CSDL.
- [x] **Thêm sách mới (`/books/add`):** Form có dropdown chọn danh mục, nhập Tên sách, Tác giả, Năm xuất bản, Đơn giá, Số lượng, Công tắc trạng thái sẵn sàng. Tự động gán khóa ngoại `category_id`.
- [x] **Chỉnh sửa sách (`/books/edit/<id>`):** Cập nhật mọi trường dữ liệu và chuyển đổi danh mục cho cuốn sách.
- [x] **Xóa sách (`/books/delete/<id>`):** Xóa sách khỏi cơ sở dữ liệu.

### 1.3. Dashboard quản lý danh mục sách và sách (`/` & `/dashboard`)
- [x] **4 Thẻ số liệu thống kê (Stat Cards):**
  - Tổng số danh mục hiện có.
  - Tổng số đầu sách trong kho.
  - Số sách sẵn sàng cho mượn và số sách hết hàng.
  - Tổng giá trị định giá kho sách theo số lượng và đơn giá (format VNĐ).
- [x] **Biểu đồ trực quan (Chart.js):** Biểu đồ hình vành khuyên (Doughnut Chart) thể hiện tỷ lệ % phân bố sách giữa các danh mục.
- [x] **Bảng thống kê tỷ lệ:** Bảng thanh tiến trình (Progress Bar) thể hiện tỷ lệ phần trăm và tổng giá trị từng danh mục.
- [x] **Bảng sách mới cập nhật gần đây:** 5 cuốn sách được thêm mới nhất kèm thao tác nhanh.

### 1.4. Cơ sở dữ liệu SQLite & SQLAlchemy 2.0
- [x] **Lưu trữ bền vững:** CSDL SQLite lưu tại `instance/library.db`.
- [x] **Cú pháp hiện đại:** Sử dụng `Mapped`, `mapped_column`, quan hệ `relationship("Book", back_populates="category")`, khóa ngoại `ForeignKey("categories.id")`.
- [x] **Seed Data:** Tự động tạo bảng (`db.create_all()`) và nạp 5 danh mục cùng 11 đầu sách mẫu kinh điển phong phú khi khởi chạy lần đầu.
- [x] **Hệ thống RESTful API:** Cung cấp các endpoint JSON:
  - `/api/dashboard/stats`: Thống kê tổng quan.
  - `/api/categories`: Danh sách danh mục dạng JSON.
  - `/api/books`: Danh sách sách dạng JSON (hỗ trợ lọc `?category_id=...`).
  - `/api/books/<id>`: Chi tiết sách dạng JSON.

---

## 2. Cấu trúc thư mục dự án

```text
BaiKiemTra/
├── .gitignore                  # Bỏ qua .venv, instance/*.db, __pycache__
├── requirements.txt            # Khai báo Flask, Flask-SQLAlchemy
├── app.py                      # Ứng dụng chính Flask + Models + Routes CRUD + APIs
├── test_app.py                 # Bộ Unit Test tự động (14/14 test cases pass)
├── README.md                   # Tài liệu báo cáo & kiểm thử
├── instance/
│   └── library.db              # File cơ sở dữ liệu SQLite tự sinh
└── templates/
    ├── base.html               # Layout khung Bootstrap 5, navbar, footer
    ├── dashboard.html          # Trang Dashboard tổng quan + Chart.js
    ├── categories/
    │   ├── index.html          # Danh sách danh mục
    │   ├── add.html            # Form thêm danh mục
    │   └── edit.html           # Form sửa danh mục
    └── books/
        ├── index.html          # Danh sách sách + bộ lọc đa năng
        ├── detail.html         # Trang chi tiết sách
        ├── add.html            # Form thêm sách có chọn danh mục
        └── edit.html           # Form chỉnh sửa sách
```

---

## 3. Hướng dẫn khởi chạy ứng dụng

### Bước 1: Di chuyển vào thư mục bài kiểm tra
```powershell
cd BaiKiemTra
```

### Bước 2: Kích hoạt môi trường ảo (.venv)
- Trên PowerShell:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- Trên Command Prompt (CMD):
  ```cmd
  .\.venv\Scripts\activate.bat
  ```

### Bước 3: Cài đặt thư viện (nếu chạy trên máy mới)
```powershell
pip install -r requirements.txt
```

### Bước 4: Khởi chạy ứng dụng
```powershell
python app.py
```
Ứng dụng sẽ tự động khởi tạo CSDL SQLite tại `instance/library.db` và chạy tại: **`http://127.0.0.1:5000/`**

---

## 4. Chạy kiểm thử tự động (Unit Test)

Dự án tích hợp sẵn 14 kịch bản kiểm thử tự động bao quát toàn bộ Dashboard, CRUD Danh mục, CRUD Sách và REST API:

```powershell
python test_app.py
```

*Kết quả mong đợi:*
```text
..............
----------------------------------------------------------------------
Ran 14 tests in 0.185s

OK
```

---

## 5. Các lệnh `curl` kiểm thử kiểm tra nhanh

### 5.1. Kiểm tra Dashboard
```bash
curl -i http://127.0.0.1:5000/
```
*Kết quả:* Mã 200 OK, trả về giao diện Dashboard tổng quan.

### 5.2. Kiểm tra API Thống kê
```bash
curl -i http://127.0.0.1:5000/api/dashboard/stats
```
*Kết quả:* Mã 200 OK, JSON chứa `total_categories`, `total_books`, `available_books`, `total_inventory_value`.

### 5.3. Kiểm tra API Danh mục
```bash
curl -i http://127.0.0.1:5000/api/categories
```
*Kết quả:* Mã 200 OK, trả về danh sách 5 danh mục ban đầu.

### 5.4. Kiểm tra API Sách (lọc theo danh mục CNTT - id=1)
```bash
curl -i "http://127.0.0.1:5000/api/books?category_id=1"
```
*Kết quả:* Mã 200 OK, trả về danh sách sách thuộc danh mục Công nghệ thông tin.

### 5.5. Kiểm tra API Chi tiết sách ID = 1
```bash
curl -i http://127.0.0.1:5000/api/books/1
```
*Kết quả:* Mã 200 OK, thông tin sách "Lập trình Python từ cơ bản đến nâng cao".
