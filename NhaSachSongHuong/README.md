# 📖 Nhà Sách Trực Tuyến Sông Hương (NhaSachSongHuong)
> **Bài tập tổng hợp Chương 5 – 6: Giỏ hàng · Đặt hàng · Quản trị sách, danh mục, đơn hàng**  
> **Học phần:** Phần mềm mã nguồn mở — Khoa Công nghệ Thông tin, Trường Đại học Khoa học, Đại học Huế (HUSC).  
> **Giảng viên:** ThS. Nguyễn Dũng

---

## 🌟 Giới thiệu Hệ thống

Hệ thống **Nhà sách Sông Hương** là một ứng dụng web thương mại điện tử hoàn chỉnh được xây dựng trên nền tảng **Python / Flask 3**, tuân thủ nghiêm ngặt mô hình kiến trúc MVC, bảo mật phiên làm việc và chuẩn ORM **SQLAlchemy 2.0**.

Ứng dụng đáp ứng đầy đủ **11 màn hình nghiệp vụ** được quy định chi tiết trong tài liệu bài tập:
- **Phần A (Storefront - Khách mua sách):** 5 màn hình từ xem danh mục, duyệt chi tiết sách, thao tác giỏ hàng, đặt hàng thanh toán và nhận biên nhận đơn hàng.
- **Phần B (Admin Portal - Quản trị viên):** 6 màn hình từ tổng quan Dashboard thống kê động, quản lý đầu sách và upload ảnh bìa, phân loại danh mục, theo dõi danh sách đơn hàng đến máy trạng thái xử lý đơn hàng chuyên sâu.

---

## 🛠 Công nghệ Sử dụng

| Thành phần | Công nghệ / Thư viện | Vai trò |
|---|---|---|
| **Backend** | Python 3.11+, Flask 3.0+ | Bộ khung ứng dụng web, điều hướng Route, Session management |
| **ORM & Database** | Flask-SQLAlchemy 3.1+, SQLite | Mô hình hóa dữ liệu quan hệ, quan hệ 1-N, N-N, Transaction ACID |
| **Biểu mẫu & Bảo mật** | Flask-WTF, WTForms, Email-Validator | Quản lý Form, Token CSRF, Regex validation, Kiểm tra trùng lặp |
| **Frontend** | Jinja2, Bootstrap 5.3.3, Bootstrap Icons | Giao diện Responsive hiện đại, Component UI, Modal, Alert |
| **Đồ thị Thống kê** | Chart.js 4.x | Trực quan hóa doanh thu 7 ngày gần nhất trên Admin Dashboard |
| **Xử lý Tệp** | Pillow, Werkzeug Secure Filename, UUID | Tải lên ảnh bìa, định danh an toàn chống ghi đè file |
| **Kiểm thử tự động** | Python unittest | 10 bài test bao phủ toàn bộ các luồng nghiệp vụ quan trọng |

---

## 📋 Danh sách 11 Màn hình Nghiệp vụ

### Phần A. Khách Mua Hàng (Customer Storefront)
1. **Màn hình ①: Danh sách sách (`/books` hoặc `/`)**
   - Header cố định, hiển thị logo sách và Badge giỏ hàng màu cam đếm tổng số lượng sách đang có trong giỏ hàng theo thời gian thực.
   - Thanh bộ lọc: Tìm kiếm theo tên sách/tác giả, lọc theo từng danh mục.
   - Thẻ sách (Card): Ảnh bìa, tên sách, tác giả, giá bán định dạng VNĐ, trạng thái tồn kho ("Còn N cuốn" hoặc "Hết hàng").
   - Nút `+ Thêm vào giỏ` (Tự động khóa nếu sách hết hàng).
2. **Màn hình ②: Chi tiết sách (`/books/<id>`)**
   - Breadcrumb điều hướng: `Trang chủ` > `[Tên danh mục]` > `[Tên sách]`.
   - Ảnh bìa kích thước lớn, thông tin tác giả, nhà xuất bản, năm xuất bản, mô tả tóm tắt.
   - Bộ chọn số lượng có nút `+` và `−`, giới hạn tối đa không vượt quá số lượng tồn kho còn lại (`stock - in_cart`).
3. **Màn hình ③: Giỏ hàng (`/cart`)**
   - Lưu trữ trong Flask Session dưới dạng dictionary `{book_id_str: quantity}` (chỉ lưu ID và số lượng).
   - **Quy tắc bảo toàn giá:** Đơn giá luôn được truy vấn mới nhất từ CSDL khi hiển thị giỏ hàng, tuyệt đối không lưu giá cố định trong Session để tránh sai lệch giá khi sách điều chỉnh.
   - Nút `+` và `−` cập nhật số lượng trực tiếp theo chuẩn Post-Redirect-Get (PRG), tự động khóa tăng khi chạm mức tồn kho.
   - Nút xóa từng cuốn sách và nút `Xoá giỏ hàng` có hộp thoại xác nhận.
4. **Màn hình ④: Đặt hàng (`/checkout`)**
   - Giao diện 2 cột: Cột trái là Form Flask-WTF; cột phải là bảng tóm tắt đơn hàng.
   - Xác thực biểu mẫu chặt chẽ:
     - Số điện thoại bắt buộc 10 chữ số và bắt đầu bằng số 0 (Regex `^0\d{9}$`).
     - Tùy chọn phương thức thanh toán: `Tiền mặt khi nhận hàng (COD)` hoặc `Chuyển khoản`.
   - **Quy tắc phí vận chuyển:** Phí cố định 20.000 đ; tự động **Miễn phí (0 đ)** khi tổng tiền tạm tính từ **200.000 đ** trở lên.
   - Tự động kiểm tra lại tồn kho CSDL ngay trước khi ghi nhận đơn hàng.
5. **Màn hình ⑤: Xác nhận đặt hàng (`/orders/<id>`)**
   - Thông báo đặt hàng thành công, hiển thị mã đơn hàng, ngày tạo, thông tin giao hàng và danh sách sách đã mua kèm trạng thái ban đầu `Chờ xác nhận`.

---

### Phần B. Quản Trị Viên (Admin Portal)
6. **Màn hình ⑥: Tổng quan quản trị (`/admin` hoặc `/admin/dashboard`)**
   - Thanh điều hướng bên trái (Sidebar) chuyên nghiệp với các mục: `▣ Tổng quan`, `📚 Sách`, `🏷 Danh mục`, `🧾 Đơn hàng` (có badge số đơn chờ duyệt).
   - 4 thẻ thống kê (Stat Cards) truy vấn động:
     - Tổng số đầu sách đang quản lý.
     - Số đơn hàng đang ở trạng thái `Chờ xác nhận`.
     - Tổng doanh thu tháng hiện tại (chỉ tính các đơn `Hoàn tất`).
     - Số lượng sách sắp hết hàng (tồn kho $\le 5$).
   - Biểu đồ đường Chart.js thể hiện doanh thu 7 ngày gần nhất.
   - Bảng cảnh báo sách tồn kho thấp và 5 đơn hàng mới nhất.
7. **Màn hình ⑦: Quản lý sách (`/admin/books`)**
   - Phân trang 5 cuốn/trang, hỗ trợ giữ nguyên tham số lọc (`q`, `category_id`, `stock_filter`) khi chuyển trang.
   - Bộ lọc đa tiêu chí: Tìm theo tên/tác giả, lọc danh mục, lọc tồn kho (`Còn hàng > 5`, `Sắp hết 1-5`, `Hết hàng = 0`).
   - Sách hết hàng (= 0) được tô nền đỏ nổi bật cảnh báo.
   - **Ràng buộc an toàn:** Khóa nút Xóa nếu sách đã từng xuất hiện trong bất kỳ đơn hàng nào (`order_items`).
8. **Màn hình ⑧: Thêm & Sửa sách (`/admin/books/new` & `/admin/books/<id>/edit`)**
   - Dùng chung biểu mẫu chuẩn hóa `BookForm` với CSRF token và bắt lỗi chi tiết.
   - Kiểm tra chống trùng tên sách (case-insensitive).
   - Upload ảnh bìa: hỗ trợ file `.jpg`, `.jpeg`, `.png`, `.webp`, tự động tạo tên ngẫu nhiên UUID để chống ghi đè.
   - **Quy tắc bảo toàn giá lịch sử:** Khi quản trị viên sửa giá sách, các đơn hàng đã tạo trước đó vẫn giữ nguyên đơn giá cũ đã đóng băng trong `OrderItem.unit_price`.
9. **Màn hình ⑨: Quản lý danh mục (`/admin/categories`)**
   - Bố cục 2 cột: Cột trái hiển thị danh sách kèm số lượng sách thuộc danh mục (tính bằng truy vấn tối ưu `group_by`); Cột phải là form thêm danh mục mới.
   - Hỗ trợ sửa nhanh danh mục qua Modal popup.
   - **Ràng buộc xóa danh mục:** Hệ thống tự động chặn xóa nếu danh mục đang chứa $\ge 1$ đầu sách và hiển thị thông báo lỗi thân thiện: `✕ Không thể xoá "[Tên]": còn N sách.`
10. **Màn hình ⑩: Quản lý đơn hàng (`/admin/orders`)**
    - Hệ thống 5 tab trạng thái: `Tất cả`, `Chờ xác nhận`, `Đang giao`, `Hoàn tất`, `Đã huỷ` kèm số lượng đơn động tính bằng truy vấn `group_by`.
    - Tìm kiếm theo mã đơn, họ tên khách hàng, số điện thoại.
    - Phân trang 10 đơn/trang.
    - Dòng tổng kết ở chân bảng hiển thị tổng số đơn lọc được và tổng giá trị thanh toán tương ứng.
11. **Màn hình ⑪: Chi tiết & Xử lý đơn hàng (`/admin/orders/<id>`)**
    - Hiển thị đầy đủ thông tin khách hàng, phương thức thanh toán, địa chỉ, ghi chú và bảng mặt hàng với đơn giá đóng băng.
    - **Máy trạng thái đơn hàng (Order State Machine):**
      - `Chờ xác nhận` $\rightarrow$ `Đang giao` hoặc `Đã huỷ`.
      - `Đang giao` $\rightarrow$ `Hoàn tất` hoặc `Đã huỷ`.
      - `Hoàn tất` / `Đã huỷ`: Trạng thái cuối, form chuyển trạng thái tự động khóa.
    - **Cơ chế hoàn trả kho tự động:** Khi đơn hàng bị chuyển sang trạng thái `Đã huỷ`, hệ thống tự động cộng hoàn trả số lượng sách tương ứng vào cột `stock` của bảng `books`.
    - Nhật ký lịch sử trạng thái (Timeline) lưu vết đầy đủ thời gian, trạng thái và ghi chú xử lý của quản trị viên.

---

## 🗄 Cấu trúc Thư mục

```
NhaSachSongHuong/
├── instance/
│   └── nhasach.db              # CSDL SQLite tự động khởi tạo và nạp dữ liệu mẫu
├── static/
│   ├── css/
│   └── uploads/                # Thư mục lưu ảnh bìa sách tải lên
├── templates/
│   ├── base.html               # Layout chính cho trang bán hàng
│   ├── admin_base.html         # Layout Sidebar cho trang quản trị
│   ├── books.html              # Màn hình ①: Danh mục sách
│   ├── book_detail.html        # Màn hình ②: Chi tiết sách
│   ├── cart.html               # Màn hình ③: Giỏ hàng
│   ├── checkout.html           # Màn hình ④: Đặt hàng
│   ├── order_success.html      # Màn hình ⑤: Xác nhận đặt hàng
│   └── admin/
│       ├── dashboard.html      # Màn hình ⑥: Tổng quan quản trị
│       ├── books.html          # Màn hình ⑦: Quản lý sách
│       ├── book_form.html      # Màn hình ⑧: Thêm / Sửa sách
│       ├── categories.html     # Màn hình ⑨: Quản lý danh mục
│       ├── orders.html         # Màn hình ⑩: Quản lý đơn hàng
│       └── order_detail.html   # Màn hình ⑪: Chi tiết đơn & Máy trạng thái
├── .gitignore
├── app.py                      # File điều hướng chính chứa toàn bộ Route và Logic nghiệp vụ
├── forms.py                    # Khai báo các Form Flask-WTF và Validator
├── models.py                   # Khai báo cấu trúc Model SQLAlchemy 2.0
├── requirements.txt            # Danh sách thư viện phụ thuộc
├── test_app.py                 # Bộ kiểm thử tự động 10 Test Cases
└── README.md                   # Tài liệu hướng dẫn sử dụng chi tiết
```

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### 1. Kích hoạt môi trường ảo (Virtual Environment)
```powershell
cd D:\namtu\hocky1\mannguonmo\buoi2\NhaSachSongHuong
.\.venv\Scripts\activate
```

### 2. Cài đặt các thư viện cần thiết (nếu cài mới)
```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng Flask
```bash
python app.py
```
Ứng dụng sẽ tự động khởi tạo CSDL SQLite `instance/nhasach.db` và nạp toàn bộ 6 danh mục, 6 đầu sách và 6 đơn hàng mẫu chuẩn theo slide bài giảng.

- **Trang mua sách khách hàng:** [http://127.0.0.1:5000/books](http://127.0.0.1:5000/books)
- **Trang quản trị hệ thống:** [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)

---

## 🧪 Chạy Kiểm Thử Tự Động (Unit Tests)

Bộ test tự động `test_app.py` kiểm tra toàn bộ 10 kịch bản:
```powershell
python test_app.py
```
**Kết quả kiểm thử:**
```
Ran 10 tests in 0.352s
OK
```
Bao gồm:
1. `test_01_catalog_view_and_filter`: Xem danh mục sách, lọc thể loại, tìm kiếm từ khóa.
2. `test_02_book_detail_and_stock_badge`: Chi tiết sách và hiển thị trạng thái tồn kho / hết hàng.
3. `test_03_cart_operations`: Thêm giỏ hàng, cập nhật tăng/giảm số lượng, xóa sách, dọn sạch giỏ.
4. `test_04_checkout_and_order_creation`: Đặt hàng thành công, trừ kho tự động, áp dụng freeship $\ge 200\text{k}$.
5. `test_05_admin_dashboard`: Kiểm tra 4 thẻ thống kê và canvas biểu đồ doanh thu.
6. `test_06_admin_books_crud_and_safety_rule`: Thêm/sửa sách, chặn trùng tên, chặn xóa sách đã có đơn hàng.
7. `test_07_admin_categories_and_safety_rule`: Thêm danh mục, chặn xóa danh mục đang có sách.
8. `test_08_admin_orders_and_state_machine`: Chuyển trạng thái đơn và tự động hoàn trả tồn kho khi hủy đơn.
9. `test_09_checkout_phone_validation_regex`: Bắt lỗi định dạng số điện thoại theo chuẩn Regex.
10. `test_10_admin_orders_filter_and_search`: Lọc đơn hàng theo tab trạng thái và tìm kiếm khách hàng.
