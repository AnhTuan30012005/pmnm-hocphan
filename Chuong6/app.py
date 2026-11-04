from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

# Header trả về văn bản thuần để trình duyệt không hiểu nhầm <Student ...> là thẻ HTML
TEXT = {"Content-Type": "text/plain; charset=utf-8"}

# Khởi tạo extension SQLAlchemy
db = SQLAlchemy()

app = Flask(__name__)
# Cấu hình đường dẫn CSDL SQLite chuẩn theo slide: instance/qlsv.db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///qlsv.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "secret-key-chuong6-pmnm"

# Khởi tạo ứng dụng với db
db.init_app(app)


# Bước 3: Khai báo model Student
class Student(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    mssv: Mapped[str] = mapped_column(String(10), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    gpa: Mapped[float] = mapped_column(default=0.0)

    def __repr__(self):
        return f"<Student {self.mssv} {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "mssv": self.mssv,
            "name": self.name,
            "gpa": self.gpa
        }


# Tự động tạo bảng khi khởi động app
with app.app_context():
    db.create_all()


# Bước 5: Thêm dữ liệu bằng view function (Route tạm thời theo slide)
@app.get("/them-mau")
def add_sample():
    total = db.session.scalar(
        db.select(func.count(Student.id)))
    if total > 0:
        return f"Đã có {total} sinh viên, không thêm nữa."
    an = Student(mssv="23T1020001",
                 name="Nguyễn Văn An", gpa=8.5)
    before = an.id                  # chưa ghi xuống CSDL
    db.session.add(an)              # đưa vào "giỏ" chờ ghi
    db.session.add_all([
        Student(mssv="23T1020002", name="Trần Thị Bình", gpa=6.8),
        Student(mssv="23T1020003", name="Lê Hoàng Cường", gpa=9.1),
        Student(mssv="23T1020004", name="Phạm Minh Dũng", gpa=4.5),
        Student(mssv="23T1020005", name="Hoàng Thu Hà", gpa=7.4),
    ])
    db.session.commit()             # ghi thật sự
    return (f"Đã thêm 5 sinh viên. id của An: "
            f"trước commit = {before}, "
            f"sau commit = {an.id}")


# Bước 6: Đọc dữ liệu bằng view function
@app.get("/thu-truy-van")
def try_queries():
    if db.session.scalar(
            db.select(func.count(Student.id))) == 0:
        return "Chưa có dữ liệu, hãy mở /them-mau trước."
    lines = []
    lines.append(f"1. get(3): {db.session.get(Student, 3)}")
    lines.append(f"2. get(99): {db.session.get(Student, 99)}")
    everyone = db.session.execute(
        db.select(Student)).scalars().all()
    lines.append(f"3. Tất cả: {len(everyone)} sinh viên")
    stmt = (db.select(Student)
            .where(Student.gpa >= 8)
            .order_by(Student.gpa.desc()))
    good = db.session.execute(stmt).scalars().all()
    lines.append(f"4. Điểm >= 8: {good}")
    binh = db.session.scalar(db.select(Student)
                             .filter_by(mssv="23T1020002"))
    lines.append(f"5. MSSV 23T1020002: {binh}")
    count = db.session.scalar(
        db.select(func.count(Student.id)))
    avg = db.session.scalar(db.select(func.avg(Student.gpa)))
    lines.append(f"6. Số SV: {count}, điểm TB: {avg:.2f}")
    return "\n".join(lines), TEXT


# Trang chủ: Danh sách sinh viên
@app.route("/")
def index():
    students = Student.query.order_by(Student.id.asc()).all()
    return render_template("index.html", students=students)


# Thêm sinh viên mới (Dùng form POST)
@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        mssv = request.form.get("mssv", "").strip()
        name = request.form.get("name", "").strip()
        gpa_str = request.form.get("gpa", "").strip()

        if not mssv or not name:
            flash("Vui lòng điền đầy đủ MSSV và Họ tên!", "danger")
            return render_template("add.html", mssv=mssv, name=name, gpa=gpa_str)

        existing = Student.query.filter_by(mssv=mssv).first()
        if existing:
            flash(f"MSSV '{mssv}' đã tồn tại! Vui lòng nhập MSSV khác.", "danger")
            return render_template("add.html", mssv=mssv, name=name, gpa=gpa_str)

        try:
            gpa = float(gpa_str) if gpa_str else 0.0
            if not (0.0 <= gpa <= 10.0):
                flash("Điểm GPA phải nằm trong khoảng từ 0.0 đến 10.0!", "danger")
                return render_template("add.html", mssv=mssv, name=name, gpa=gpa_str)
        except ValueError:
            flash("GPA phải là một số thực!", "danger")
            return render_template("add.html", mssv=mssv, name=name, gpa=gpa_str)

        new_student = Student(mssv=mssv, name=name, gpa=gpa)
        db.session.add(new_student)
        db.session.commit()
        flash(f"Thêm sinh viên '{name}' ({mssv}) thành công!", "success")
        return redirect(url_for("index"))

    return render_template("add.html")


# Sửa thông tin sinh viên
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    student = db.session.get(Student, id)
    if not student:
        flash("Không tìm thấy sinh viên!", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        gpa_str = request.form.get("gpa", "").strip()

        if not name:
            flash("Họ tên không được để trống!", "danger")
            return render_template("edit.html", student=student)

        try:
            gpa = float(gpa_str) if gpa_str else 0.0
        except ValueError:
            flash("GPA phải là một số thực!", "danger")
            return render_template("edit.html", student=student)

        student.name = name
        student.gpa = gpa
        db.session.commit()
        flash(f"Cập nhật sinh viên {student.mssv} thành công!", "success")
        return redirect(url_for("index"))

    return render_template("edit.html", student=student)


# Xóa sinh viên
@app.route("/delete/<int:id>", methods=["POST"])
def delete_student(id):
    student = db.session.get(Student, id)
    if student:
        db.session.delete(student)
        db.session.commit()
        flash(f"Đã xoá sinh viên {student.mssv} - {student.name}!", "success")
    else:
        flash("Sinh viên không tồn tại!", "danger")
    return redirect(url_for("index"))


# API JSON: Lấy danh sách sinh viên
@app.route("/api/students")
def api_students():
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students])


if __name__ == "__main__":
    app.run(debug=True)
