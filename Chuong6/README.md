# CHƯƠNG 6: LÀM VIỆC VỚI CƠ SỞ DỮ LIỆU (SQLite & Flask-SQLAlchemy)

- **Môn học:** Phần mềm mã nguồn mở
- **Khoa:** Công nghệ Thông tin - Trường Đại học Khoa học, Đại học Huế
- **Chủ đề:** Khởi tạo Model, ánh xạ CSDL với SQLAlchemy 2.0 / Flask-SQLAlchemy 3.x, CRUD Quản lý Sinh viên.

---

## 1. Nội dung hoàn thành

- [x] **Bước 1: Cài đặt thư viện**
  - Cài đặt `Flask` và `flask-sqlalchemy` (phiên bản `>=3.1.0` hỗ trợ cú pháp SQLAlchemy 2.0).
- [x] **Bước 2: Cấu hình kết nối CSDL SQLite**
  - Khởi tạo extension `db = SQLAlchemy()`.
  - Cấu hình `SQLALCHEMY_DATABASE_URI = "sqlite:///qlsv.db"` (file lưu tại `instance/qlsv.db`).
  - Gọi `db.init_app(app)`.
- [x] **Bước 3: Khai báo Model `Student` (Đúng chuẩn slide giảng dạy)**
  - `id: Mapped[int] = mapped_column(primary_key=True)` (Khoá chính, tự tăng).
  - `mssv: Mapped[str] = mapped_column(String(10), unique=True)` (Duy nhất, tối đa 10 ký tự).
  - `name: Mapped[str] = mapped_column(String(100))` (Họ tên sinh viên).
  - `gpa: Mapped[float] = mapped_column(default=0.0)` (Điểm số thực, mặc định 0.0).
  - Phương thức `__repr__` hỗ trợ in định dạng `<Student {mssv} {name}>`.
- [x] **Bước 4: Tạo bảng SQLite**
  - Gọi `db.create_all()` trong context `app.app_context()`.
- [x] **Bước 5: Thêm dữ liệu bằng view function (`/them-mau`)**
  - Kiểm tra `total = db.session.scalar(db.select(func.count(Student.id)))`.
  - Nếu `total > 0`: Trả về `"Đã có {total} sinh viên, không thêm nữa."`.
  - Ngược lại: Thêm sinh viên An (`db.session.add(an)`) và 4 sinh viên còn lại (`db.session.add_all(...)`), sau đó `db.session.commit()`.
  - Thấy rõ sự khác biệt của `an.id`: trước commit là `None`, sau commit được SQLite cấp `1`.
- [x] **Bước 6: Đọc dữ liệu bằng view function (`/thu-truy-van`)**
  - Khai báo header trả về văn bản thuần `TEXT = {"Content-Type": "text/plain; charset=utf-8"}` để trình duyệt không nuốt các thẻ `<Student ...>`.
  - Kiểm tra bảng rỗng trước để tránh lỗi định dạng `avg:.2f` khi `avg` là `None`.
  - `db.session.get(Student, 3)`: Lấy theo khóa chính ID = 3.
  - `db.session.get(Student, 99)`: ID không tồn tại trả về `None`, không gây lỗi.
  - `db.session.execute(db.select(Student)).scalars().all()`: Lấy danh sách tất cả sinh viên.
  - `db.select(Student).where(Student.gpa >= 8).order_by(Student.gpa.desc())`: Lọc theo điều kiện `where` và sắp xếp `order_by`.
  - `db.session.scalar(db.select(Student).filter_by(mssv="23T1020002"))`: Tìm sinh viên theo MSSV bằng `filter_by`.
  - `func.count(Student.id)` và `func.avg(Student.gpa)`: Hàm đếm và tính điểm trung bình chuẩn SQL.
- [x] **Bước mở rộng: Xây dựng các chức năng CRUD & Giao diện**
  - `GET /`: Hiển thị danh sách sinh viên dạng bảng với Bootstrap 5.
  - `GET, POST /add`: Form thêm sinh viên mới, kiểm tra lỗi trùng MSSV và GPA hợp lệ.
  - `GET, POST /edit/<id>`: Sửa thông tin họ tên, GPA của sinh viên.
  - `POST /delete/<id>`: Xóa sinh viên khỏi cơ sở dữ liệu.
  - `GET /api/students`: API trả về danh sách sinh viên dưới dạng JSON.

---

## 2. Hướng dẫn khởi chạy

### Bước 2.1: Kích hoạt môi trường ảo
```powershell
cd Chuong6
.\.venv\Scripts\Activate.ps1
```

### Bước 2.2: Cài đặt thư viện (nếu thiết lập máy mới)
```powershell
pip install -r requirements.txt
```

### Bước 2.3: Khởi chạy ứng dụng
```powershell
python app.py
# hoặc: flask --app app run --debug
```
Ứng dụng sẽ tự động khởi tạo file CSDL SQLite tại `instance/qlsv.db` và chạy tại: `http://127.0.0.1:5000/`

---

## 3. Các lệnh kiểm thử & curl

### 3.1. Chạy Unit Test tự động
```powershell
python test_app.py
```

### 3.2. Kiểm thử Route `/them-mau`
- **Lần 1:** Truy cập `http://127.0.0.1:5000/them-mau`
  - *Kết quả:* `Đã thêm 5 sinh viên. id của An: trước commit = None, sau commit = 1`
- **Lần 2:** Tải lại trang `http://127.0.0.1:5000/them-mau`
  - *Kết quả:* `Đã có 5 sinh viên, không thêm nữa.`

### 3.3. Kiểm thử Route `/thu-truy-van`
Truy cập `http://127.0.0.1:5000/thu-truy-van`
*Kết quả:*
```text
1. get(3): <Student 23T1020003 Lê Hoàng Cường>
2. get(99): None
3. Tất cả: 5 sinh viên
4. Điểm >= 8: [<Student 23T1020003 Lê Hoàng Cường>, <Student 23T1020001 Nguyễn Văn An>]
5. MSSV 23T1020002: <Student 23T1020002 Trần Thị Bình>
6. Số SV: 5, điểm TB: 7.26
```

### 3.4. Kiểm tra Route Danh sách HTML (`/`)
```bash
curl -i http://127.0.0.1:5000/
```
*Kết quả:* Mã 200 OK, trả về giao diện bảng danh sách sinh viên.

### 3.4. Kiểm tra API JSON (`/api/students`)
```bash
curl -i http://127.0.0.1:5000/api/students
```
*Kết quả:* Mã 200 OK, `Content-Type: application/json`.
