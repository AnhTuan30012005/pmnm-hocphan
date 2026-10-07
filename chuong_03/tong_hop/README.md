# BÀI TẬP TỔNG HỢP CHƯƠNG 3: SỔ ĐIỂM LỚP HỌC

* **Học phần:** Phần mềm mã nguồn mở
* **Khoa:** Công nghệ Thông tin - Trường Đại học Khoa học, Đại học Huế
* **Mã nguồn:** `chuong_03/tong_hop/`

---

## 1. Hướng dẫn khởi chạy

Cài đặt thư viện:
```bash
pip install -r requirements.txt
```

Khởi chạy ứng dụng:
```bash
python -m flask --app sodiem run --debug --port 8000
```
Hoặc:
```bash
python sodiem.py
```

Truy cập giao diện web tại: `http://127.0.0.1:8000/`

---

## 2. Kết quả `flask --app sodiem routes`

Lệnh thực thi:
```bash
python -m flask --app sodiem routes
```

Kết quả hiển thị (đúng 10 dòng endpoint/rule kể cả static):
```text
Endpoint              Methods           Rule                                
--------------------  ----------------  ------------------------------------
api_student_detail    GET               /api/students/<mssv>                
api_students          GET               /api/students                       
export_student_csv    GET               /students/<mssv>/export             
home                  GET               /                                   
search                GET               /search                             
short_student_detail  GET               /sv/<mssv>                          
static                GET               /static/<path:filename>             
student_course_score  DELETE, GET, PUT  /api/students/<mssv>/scores/<course>
student_detail        GET               /students/<mssv>                    
student_list          GET               /students                           
```

---

## 3. Dòng trạng thái và body của từng lệnh `curl`

Biến môi trường kiểm thử:
```bash
B=http://127.0.0.1:8000
S=$B/api/students/23T1020005/scores
```

### 3.1. `curl -i $B/sv/23T1020001` (# 301)
* **Lệnh:**
  ```bash
  curl -i http://127.0.0.1:8000/sv/23T1020001
  ```
* **Dòng trạng thái & Header quan trọng:**
  ```http
  HTTP/1.1 301 MOVED PERMANENTLY
  Location: /students/23T1020001
  Content-Type: text/html; charset=utf-8
  ```
* **Body:**
  ```html
  <!doctype html>
  <html lang=en>
  <title>Redirecting...</title>
  <h1>Redirecting...</h1>
  <p>You should be redirected automatically to the target URL: <a href="/students/23T1020001">/students/23T1020001</a>. If not, click the link.
  ```

---

### 3.2. `curl -i $B/students/23T1020001/export` (# CSV)
* **Lệnh:**
  ```bash
  curl -i http://127.0.0.1:8000/students/23T1020001/export
  ```
* **Dòng trạng thái & Header quan trọng:**
  ```http
  HTTP/1.1 200 OK
  Content-Type: text/csv; charset=utf-8
  Content-Disposition: attachment; filename=diem_23T1020001.csv
  ```
* **Body:**
  ```csv
  hoc_phan,diem
  PMMNM,8.5
  CSDL,7.0
  MMT,9.0
  ```

---

### 3.3. `curl "$B/api/students?lop=k47a&min_avg=7"`
* **Lệnh:**
  ```bash
  curl "http://127.0.0.1:8000/api/students?lop=k47a&min_avg=7"
  ```
* **Dòng trạng thái & Header quan trọng:**
  ```http
  HTTP/1.1 200 OK
  Content-Type: application/json
  ```
* **Body:**
  ```json
  [
    {
      "average": 8.17,
      "lop": "K47A",
      "mssv": "23T1020001",
      "name": "Nguyễn Văn An",
      "rank": "Khá",
      "scores": {
        "CSDL": 7.0,
        "MMT": 9.0,
        "PMMNM": 8.5
      }
    }
  ]
  ```

---

### 3.4. `curl -i "$B/api/students?min_avg=abc"` (# 400)
* **Lệnh:**
  ```bash
  curl -i "http://127.0.0.1:8000/api/students?min_avg=abc"
  ```
* **Dòng trạng thái & Header quan trọng:**
  ```http
  HTTP/1.1 400 BAD REQUEST
  Content-Type: application/json
  ```
* **Body:**
  ```json
  {
    "detail": "min_avg phải là một số thực.",
    "error": "Dữ liệu không hợp lệ"
  }
  ```

---

### 3.5. `curl -i $B/api/students/999` (# 404)
* **Lệnh:**
  ```bash
  curl -i http://127.0.0.1:8000/api/students/999
  ```
* **Dòng trạng thái & Header quan trọng:**
  ```http
  HTTP/1.1 404 NOT FOUND
  Content-Type: application/json
  ```
* **Body:**
  ```json
  {
    "detail": "Không có sinh viên với MSSV = 999.",
    "error": "Không tìm thấy"
  }
  ```

---

### 3.6. `curl -i -X PUT "$S/web?score=9"` (# 201)
* **Lệnh:**
  ```bash
  curl -i -X PUT "http://127.0.0.1:8000/api/students/23T1020005/scores/web?score=9"
  ```
* **Dòng trạng thái & Header quan trọng:**
  ```http
  HTTP/1.1 201 CREATED
  Location: /api/students/23T1020005/scores/WEB
  Content-Type: application/json
  ```
* **Body:**
  ```json
  {
    "average": 9.0,
    "course": "WEB",
    "mssv": "23T1020005",
    "score": 9
  }
  ```

---

### 3.7. `curl -X PUT "$S/WEB?score=7.5"` (# 200)
* **Lệnh:**
  ```bash
  curl -X PUT "http://127.0.0.1:8000/api/students/23T1020005/scores/WEB?score=7.5"
  ```
* **Dòng trạng thái & Header quan trọng:**
  ```http
  HTTP/1.1 200 OK
  Content-Type: application/json
  ```
* **Body:**
  ```json
  {
    "average": 7.5,
    "course": "WEB",
    "mssv": "23T1020005",
    "score": 7.5
  }
  ```

---

### 3.8. `curl -i -X PUT "$S/WEB?score=11"` (# 400)
* **Lệnh:**
  ```bash
  curl -i -X PUT "http://127.0.0.1:8000/api/students/23T1020005/scores/WEB?score=11"
  ```
* **Dòng trạng thái & Header quan trọng:**
  ```http
  HTTP/1.1 400 BAD REQUEST
  Content-Type: application/json
  ```
* **Body:**
  ```json
  {
    "detail": "score phải nằm trong đoạn [0, 10].",
    "error": "Dữ liệu không hợp lệ"
  }
  ```

---

### 3.9. `curl -i -X DELETE $S/WEB` (# 204)
* **Lệnh:**
  ```bash
  curl -i -X DELETE http://127.0.0.1:8000/api/students/23T1020005/scores/WEB
  ```
* **Dòng trạng thái & Header quan trọng:**
  ```http
  HTTP/1.1 204 NO CONTENT
  Content-Type: text/html; charset=utf-8
  ```
* **Body:**
  *(Rỗng - Empty Body)*

---

### 3.10. `curl -i -X POST $S/WEB` (# 405 JSON)
* **Lệnh:**
  ```bash
  curl -i -X POST http://127.0.0.1:8000/api/students/23T1020005/scores/WEB
  ```
* **Dòng trạng thái & Header quan trọng:**
  ```http
  HTTP/1.1 405 METHOD NOT ALLOWED
  Content-Type: application/json
  ```
* **Body:**
  ```json
  {
    "detail": "The method is not allowed for the requested URL.",
    "error": "Phương thức không được hỗ trợ"
  }
  ```

---

### 3.11. `curl -i -X POST $B/students` (# 405 HTML)
* **Lệnh:**
  ```bash
  curl -i -X POST http://127.0.0.1:8000/students
  ```
* **Dòng trạng thái & Header quan trọng:**
  ```http
  HTTP/1.1 405 METHOD NOT ALLOWED
  Content-Type: text/html; charset=utf-8
  ```
* **Body:**
  *(Trang HTML hoàn chỉnh qua khung `layout()`, chứa thông báo lỗi:)*
  ```html
  <div style="text-align: center; padding: 32px 16px;">
      <h2 style="color: #dc2626; font-size: 1.6rem; margin-bottom: 12px;">Lỗi 405: Phương thức không được hỗ trợ</h2>
      <p style="color: #475569; font-size: 1.05rem; margin-bottom: 24px;">The method is not allowed for the requested URL.</p>
      <p><a href="/" class="btn">← Quay lại Trang chủ</a></p>
  </div>
  ```

---

## 4. Trả lời các câu hỏi lý thuyết

### 4.1. Vì sao Câu 4 dùng 301 còn Câu 8 trả 201 kèm Location?
* **Câu 4 dùng mã `301 Moved Permanently`:**
  * Đây là cơ chế **chuyển hướng URL vĩnh viễn** (URL Redirection / Alias) từ đường dẫn ngắn `/sv/<mssv>` sang đường dẫn đầy đủ `/students/<mssv>`.
  * Trình duyệt và các công cụ tìm kiếm khi nhận được mã 301 sẽ tự động điều hướng sang địa chỉ mới, đồng thời lưu vào bộ nhớ đệm (cache) để các lần truy cập tiếp theo sẽ gọi thẳng đến URL đích mà không cần qua bước chuyển tiếp nữa.
* **Câu 8 dùng mã `201 Created` kèm header `Location`:**
  * Đây là thao tác **tạo mới tài nguyên** (thêm học phần và điểm số mới cho sinh viên qua phương thức `PUT`).
  * Theo chuẩn thiết kế RESTful API (RFC 7231 / RFC 9110), khi một tài nguyên mới được tạo thành công, máy chủ phải trả về mã trạng thái `201 Created` và gửi kèm header `Location` chứa URI trỏ trực tiếp đến tài nguyên vừa được tạo (ở đây là URL truy vấn điểm của học phần đó: `/api/students/<mssv>/scores/<course>`).

### 4.2. Thêm điểm cho 23T1020005 rồi khởi động lại server, điểm đó còn không? Vì sao?
* **Trả lời:** Điểm đó **KHÔNG CÒN** (bị mất và quay về danh sách rỗng `{}`).
* **Giải thích:**
  * Toàn bộ dữ liệu của chương trình hiện tại được lưu trữ trong biến từ điển `STUDENTS` trên bộ nhớ trong (**RAM**) của tiến trình Python đang chạy, chứ chưa được lưu trữ bền vững (**persistent storage**) vào cơ sở dữ liệu (Database như SQLite, MySQL, PostgreSQL,...) hay file lưu trữ vật lý (JSON, CSV,...).
  * Khi tiến trình máy chủ Flask dừng lại hoặc khởi động lại, toàn bộ không gian bộ nhớ RAM được cấp phát cho tiến trình sẽ bị giải phóng. Khi máy chủ chạy lại từ đầu, từ điển `STUDENTS` được gán lại bằng giá trị khởi tạo ban đầu được định nghĩa trong mã nguồn `sodiem.py`.

### 4.3. (Câu hỏi mở rộng Slide 16) Vì sao dùng được `request` trong hàm `handle_error` dù nó không phải là view function?
* **Giải thích:**
  * Trong kiến trúc Flask, `request` không phải là một tham số cục bộ mà là một **Context Proxy** tham chiếu đến context của HTTP request hiện tại (`RequestContext`).
  * Khi có bất kỳ một HTTP request nào gửi đến, Flask sẽ tạo và kích hoạt `RequestContext` trước khi định tuyến và gọi view function. Ngữ cảnh này được duy trì xuyên suốt toàn bộ chu trình sống của request, kể cả khi phát sinh ngoại lệ (Exception / HTTP error) và luồng thực thi chuyển sang hàm xử lý lỗi `@app.errorhandler`.
  * Nhờ vậy, trong hàm xử lý lỗi, `request` vẫn còn hiệu lực và có thể truy xuất các thuộc tính như `request.path`, `request.method`,... như bình thường.
