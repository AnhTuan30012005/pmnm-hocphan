# LibraryMS v0.1 - Bài tập dự án Chương 3 (Flask căn bản)

Môn học: **Phần mềm mã nguồn mở**  
Khoa Công nghệ Thông tin - Trường Đại học Khoa học, Đại học Huế  
Phiên bản tag: **`v0.1`**

---

## 1. Yêu cầu đã hoàn thành
- [x] Danh sách `BOOKS` >= 4 cuốn: có đủ 6 trường `id`, `title`, `author`, `year`, `category`, `available`.
- [x] `/`: Tổng số đầu sách, số sách sẵn sàng cho mượn.
- [x] `/books`: Bảng sách, tên sách liên kết đến trang chi tiết; lọc `?category=Lập trình` kèm thanh liên kết theo thể loại.
- [x] `/books/<int:book_id>`: Trang chi tiết sách; ID không tồn tại -> mã 404 `"Không có sách với ID = ..."`.
- [x] `/api/books`, `/api/books/<int:book_id>`: JSON; không tồn tại -> `{"error": "..."}` với mã 404.
- [x] Trang 404 tùy biến, có menu chung (phân biệt HTML và API JSON).
- [x] Mọi liên kết dùng `url_for`, mọi dữ liệu chèn vào HTML đều `escape`.
- [x] Mã nguồn mộc mạc, rõ ràng, không lặp (dùng hàm `menu_chung()` và `find_book()`).
- [x] Đã commit và gắn tag `v0.1`.

---

## 2. Hướng dẫn khởi chạy

Cài đặt Flask (nếu chưa có):
```bash
pip install flask
```

Khởi chạy ứng dụng bằng lệnh:
```bash
flask --app app run
```
Hoặc:
```bash
python app.py
```
Truy cập tại: `http://127.0.0.1:5000/`

---

## 3. Các lệnh `curl` và URL đã dùng để kiểm thử

### 3.1. Route `/` (Trang chủ)
```bash
curl -i http://127.0.0.1:5000/
```
*Kết quả:* Mã 200 OK, hiển thị menu chung, tổng số đầu sách (4) và số sách sẵn sàng (3).

### 3.2. Route `/books` (Danh sách sách)
```bash
curl -i http://127.0.0.1:5000/books
```
*Kết quả:* Mã 200 OK, thanh liên kết các thể loại và bảng sách kèm link chi tiết.

### 3.3. Lọc theo thể loại `/books?category=...`
```bash
curl -i -G "http://127.0.0.1:5000/books" --data-urlencode "category=Lập trình"
```
*Kết quả:* Mã 200 OK, bảng chỉ hiển thị 2 cuốn sách thể loại Lập trình.

### 3.4. Route `/books/<int:book_id>` (Chi tiết sách tồn tại)
```bash
curl -i http://127.0.0.1:5000/books/1
```
*Kết quả:* Mã 200 OK, chi tiết cuốn sách ID = 1.

### 3.5. Route `/books/<int:book_id>` (Không tồn tại -> 404 HTML có menu chung)
```bash
curl -i http://127.0.0.1:5000/books/999
```
*Kết quả:* Mã 404 NOT FOUND, trang HTML tùy biến có menu chung và dòng thông báo: `"Không có sách với ID = 999"`.

### 3.6. Route `/api/books` (Danh sách JSON)
```bash
curl -i http://127.0.0.1:5000/api/books
```
*Kết quả:* Mã 200 OK, Content-Type: application/json.

### 3.7. Route `/api/books?category=...` (Lọc JSON)
```bash
curl -i -G "http://127.0.0.1:5000/api/books" --data-urlencode "category=Lập trình"
```
*Kết quả:* Mã 200 OK, JSON danh sách sách thể loại Lập trình.

### 3.8. Route `/api/books/<int:book_id>` (Chi tiết JSON)
```bash
curl -i http://127.0.0.1:5000/api/books/1
```
*Kết quả:* Mã 200 OK, JSON thông tin sách ID = 1.

### 3.9. Route `/api/books/<int:book_id>` (Không tồn tại -> 404 JSON)
```bash
curl -i http://127.0.0.1:5000/api/books/999
```
*Kết quả:* Mã 404 NOT FOUND, JSON:
```json
{
  "error": "Không có sách với ID = 999"
}
```

---

## 4. Kiểm thử tự động (Unit Test)
Chạy lệnh:
```bash
python test_app.py
```
Kết quả:
```text
Ran 12 tests in 0.027s
OK
```
