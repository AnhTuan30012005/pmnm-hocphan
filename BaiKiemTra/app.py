import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, func, desc
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Khởi tạo extension SQLAlchemy
db = SQLAlchemy()

app = Flask(__name__)
# Cấu hình CSDL SQLite tại instance/library.db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "secret-key-bai-kiem-tra-pmnm-2026"

db.init_app(app)


# ==========================================
# 1. CSDL SQLITE VÀ CÁC MODEL (SQLAlchemy 2.0)
# ==========================================

class Category(db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Quan hệ 1-N với Book (Cascade delete: Xóa danh mục sẽ xóa sách thuộc danh mục đó)
    books: Mapped[list["Book"]] = relationship(
        "Book", back_populates="category", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self):
        return f"<Category {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "book_count": len(self.books) if self.books else 0,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class Book(db.Model):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, default=2024)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    available: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Khóa ngoại liên kết tới bảng categories
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category: Mapped["Category"] = relationship("Category", back_populates="books")

    def __repr__(self):
        return f"<Book {self.title} by {self.author}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "price": self.price,
            "quantity": self.quantity,
            "available": self.available,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


# Filter tự viết định dạng tiền tệ VNĐ
@app.template_filter("vnd")
def vnd_filter(value):
    try:
        val = int(value)
        return f"{val:,}".replace(",", ".") + " đ"
    except (ValueError, TypeError):
        return "0 đ"


# ==========================================
# 2. SEED DATA (NẠP DỮ LIỆU MẪU BAN ĐẦU)
# ==========================================
def init_db():
    with app.app_context():
        db.create_all()
        # Nạp dữ liệu mẫu nếu CSDL rỗng
        if Category.query.count() == 0:
            c1 = Category(name="Công nghệ thông tin", description="Sách lập trình, phần mềm mã nguồn mở, CSDL, AI và Web")
            c2 = Category(name="Kinh tế & Khởi nghiệp", description="Tài chính, quản trị kinh doanh, marketing và phát triển dự án")
            c3 = Category(name="Văn học & Nghệ thuật", description="Tiểu thuyết, truyện ngắn, thơ ca và tác phẩm kinh điển")
            c4 = Category(name="Khoa học & Vũ trụ", description="Vật lý, thiên văn, sinh học và khám phá tự nhiên")
            c5 = Category(name="Kỹ năng sống", description="Tư duy phát triển bản thân, kỹ năng giao tiếp và lãnh đạo")

            db.session.add_all([c1, c2, c3, c4, c5])
            db.session.commit()

            sample_books = [
                Book(title="Lập trình Python từ cơ bản đến nâng cao", author="Nguyễn Dũng", year=2023, price=125000, quantity=15, available=True, category_id=c1.id),
                Book(title="Xây dựng ứng dụng Web với Flask", author="Nguyễn Anh Tuấn", year=2024, price=145000, quantity=8, available=True, category_id=c1.id),
                Book(title="Clean Code - Nghệ thuật viết code sạch", author="Robert C. Martin", year=2020, price=210000, quantity=5, available=True, category_id=c1.id),
                Book(title="Khởi nghiệp tinh gọn (The Lean Startup)", author="Eric Ries", year=2021, price=160000, quantity=10, available=True, category_id=c2.id),
                Book(title="Cha giàu Cha nghèo", author="Robert Kiyosaki", year=2019, price=135000, quantity=20, available=True, category_id=c2.id),
                Book(title="Nhà giả kim", author="Paulo Coelho", year=2020, price=79000, quantity=25, available=True, category_id=c3.id),
                Book(title="Dế Mèn phiêu lưu ký", author="Tô Hoài", year=2018, price=55000, quantity=12, available=True, category_id=c3.id),
                Book(title="Vũ trụ trong vỏ hạt dẻ", author="Stephen Hawking", year=2022, price=180000, quantity=4, available=True, category_id=c4.id),
                Book(title="Sapiens - Lược sử loài người", author="Yuval Noah Harari", year=2021, price=230000, quantity=7, available=True, category_id=c4.id),
                Book(title="Đắc nhân tâm", author="Dale Carnegie", year=2019, price=86000, quantity=30, available=True, category_id=c5.id),
                Book(title="Kỹ năng lắng nghe trong giao tiếp", author="Phạm Minh Dũng", year=2023, price=95000, quantity=0, available=False, category_id=c5.id),
            ]
            db.session.add_all(sample_books)
            db.session.commit()
            print("-> Đã khởi tạo CSDL SQLite và nạp dữ liệu mẫu thành công!")

init_db()


# ==========================================
# 3. DASHBOARD QUẢN LÝ TỔNG QUAN
# ==========================================
@app.route("/")
@app.route("/dashboard")
def dashboard():
    total_categories = Category.query.count()
    total_books = Book.query.count()
    available_books = Book.query.filter_by(available=True).count()
    out_of_stock = Book.query.filter(Book.quantity == 0).count()
    
    # Tính tổng giá trị kho sách
    total_inventory_value = db.session.scalar(
        db.select(func.sum(Book.price * Book.quantity))
    ) or 0.0

    # Thống kê phân bố sách theo từng danh mục
    categories = Category.query.all()
    cat_stats = []
    for cat in categories:
        count = len(cat.books)
        percent = (count / total_books * 100) if total_books > 0 else 0
        total_val = sum(b.price * b.quantity for b in cat.books)
        cat_stats.append({
            "category": cat,
            "count": count,
            "percent": round(percent, 1),
            "total_val": total_val
        })

    # 5 cuốn sách mới nhất
    recent_books = Book.query.order_by(Book.id.desc()).limit(5).all()

    # Dữ liệu cho biểu đồ Chart.js
    chart_labels = [c["category"].name for c in cat_stats]
    chart_data = [c["count"] for c in cat_stats]

    return render_template(
        "dashboard.html",
        total_categories=total_categories,
        total_books=total_books,
        available_books=available_books,
        out_of_stock=out_of_stock,
        total_inventory_value=total_inventory_value,
        cat_stats=cat_stats,
        recent_books=recent_books,
        chart_labels=chart_labels,
        chart_data=chart_data
    )


# ==========================================
# 4. CRUD DANH MỤC SÁCH (CATEGORIES)
# ==========================================
@app.route("/categories")
def list_categories():
    search = request.args.get("q", "").strip()
    query = Category.query
    if search:
        query = query.filter(Category.name.ilike(f"%{search}%"))
    categories = query.order_by(Category.id.asc()).all()
    return render_template("categories/index.html", categories=categories, search=search)


@app.route("/categories/add", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Tên danh mục không được để trống!", "danger")
            return render_template("categories/add.html", name=name, description=description)

        # Kiểm tra trùng tên danh mục
        existing = Category.query.filter_by(name=name).first()
        if existing:
            flash(f"Danh mục '{name}' đã tồn tại! Vui lòng chọn tên khác.", "warning")
            return render_template("categories/add.html", name=name, description=description)

        new_cat = Category(name=name, description=description)
        db.session.add(new_cat)
        db.session.commit()
        flash(f"Thêm danh mục '{name}' thành công!", "success")
        return redirect(url_for("list_categories"))

    return render_template("categories/add.html")


@app.route("/categories/edit/<int:id>", methods=["GET", "POST"])
def edit_category(id):
    cat = db.session.get(Category, id)
    if not cat:
        flash("Không tìm thấy danh mục yêu cầu!", "danger")
        return redirect(url_for("list_categories"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Tên danh mục không được để trống!", "danger")
            return render_template("categories/edit.html", category=cat)

        existing = Category.query.filter(Category.name == name, Category.id != id).first()
        if existing:
            flash(f"Tên danh mục '{name}' đã bị trùng!", "warning")
            return render_template("categories/edit.html", category=cat)

        cat.name = name
        cat.description = description
        db.session.commit()
        flash(f"Cập nhật danh mục '{name}' thành công!", "success")
        return redirect(url_for("list_categories"))

    return render_template("categories/edit.html", category=cat)


@app.route("/categories/delete/<int:id>", methods=["POST"])
def delete_category(id):
    cat = db.session.get(Category, id)
    if cat:
        book_count = len(cat.books)
        cat_name = cat.name
        db.session.delete(cat)
        db.session.commit()
        flash(f"Đã xóa danh mục '{cat_name}' cùng {book_count} cuốn sách liên quan!", "success")
    else:
        flash("Danh mục không tồn tại!", "danger")
    return redirect(url_for("list_categories"))


# ==========================================
# 5. CRUD SÁCH THEO DANH MỤC (BOOKS)
# ==========================================
@app.route("/books")
def list_books():
    category_id = request.args.get("category_id", type=int)
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    sort = request.args.get("sort", "newest")

    query = Book.query

    # Lọc theo danh mục
    selected_category = None
    if category_id:
        selected_category = db.session.get(Category, category_id)
        if selected_category:
            query = query.filter(Book.category_id == category_id)

    # Tìm kiếm theo tên sách hoặc tác giả
    if search:
        query = query.filter((Book.title.ilike(f"%{search}%")) | (Book.author.ilike(f"%{search}%")))

    # Lọc theo trạng thái
    if status == "available":
        query = query.filter(Book.available == True)
    elif status == "out":
        query = query.filter(Book.available == False)

    # Sắp xếp
    if sort == "price_asc":
        query = query.order_by(Book.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Book.price.desc())
    elif sort == "year_desc":
        query = query.order_by(Book.year.desc())
    else:
        query = query.order_by(Book.id.desc())

    books = query.all()
    all_categories = Category.query.order_by(Category.name.asc()).all()

    return render_template(
        "books/index.html",
        books=books,
        categories=all_categories,
        selected_category=selected_category,
        search=search,
        status=status,
        sort=sort
    )


@app.route("/books/<int:id>")
def book_detail(id):
    book = db.session.get(Book, id)
    if not book:
        flash("Không tìm thấy cuốn sách yêu cầu!", "danger")
        return redirect(url_for("list_books"))
    return render_template("books/detail.html", book=book)


@app.route("/books/add", methods=["GET", "POST"])
def add_book():
    categories = Category.query.order_by(Category.name.asc()).all()
    if not categories:
        flash("Vui lòng tạo ít nhất một danh mục sách trước khi thêm sách!", "warning")
        return redirect(url_for("add_category"))

    preset_category_id = request.args.get("category_id", type=int)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        category_id = request.form.get("category_id", type=int)
        year_str = request.form.get("year", "").strip()
        price_str = request.form.get("price", "").strip()
        quantity_str = request.form.get("quantity", "").strip()
        available = True if request.form.get("available") == "on" else False

        if not title or not author or not category_id:
            flash("Vui lòng nhập đầy đủ Tên sách, Tác giả và chọn Danh mục!", "danger")
            return render_template("books/add.html", categories=categories, form=request.form)

        try:
            year = int(year_str) if year_str else 2024
            price = float(price_str) if price_str else 0.0
            quantity = int(quantity_str) if quantity_str else 1
            if quantity <= 0:
                available = False
        except ValueError:
            flash("Năm xuất bản, giá bán hoặc số lượng không hợp lệ!", "danger")
            return render_template("books/add.html", categories=categories, form=request.form)

        new_book = Book(
            title=title,
            author=author,
            category_id=category_id,
            year=year,
            price=price,
            quantity=quantity,
            available=available
        )
        db.session.add(new_book)
        db.session.commit()
        flash(f"Thêm sách '{title}' vào danh mục thành công!", "success")
        return redirect(url_for("list_books", category_id=category_id))

    return render_template("books/add.html", categories=categories, preset_category_id=preset_category_id)


@app.route("/books/edit/<int:id>", methods=["GET", "POST"])
def edit_book(id):
    book = db.session.get(Book, id)
    if not book:
        flash("Không tìm thấy cuốn sách này!", "danger")
        return redirect(url_for("list_books"))

    categories = Category.query.order_by(Category.name.asc()).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        category_id = request.form.get("category_id", type=int)
        year_str = request.form.get("year", "").strip()
        price_str = request.form.get("price", "").strip()
        quantity_str = request.form.get("quantity", "").strip()
        available = True if request.form.get("available") == "on" else False

        if not title or not author or not category_id:
            flash("Tên sách, tác giả và danh mục không được để trống!", "danger")
            return render_template("books/edit.html", book=book, categories=categories)

        try:
            year = int(year_str) if year_str else book.year
            price = float(price_str) if price_str else book.price
            quantity = int(quantity_str) if quantity_str else book.quantity
            if quantity <= 0:
                available = False
        except ValueError:
            flash("Giá bán, năm xuất bản hoặc số lượng không hợp lệ!", "danger")
            return render_template("books/edit.html", book=book, categories=categories)

        book.title = title
        book.author = author
        book.category_id = category_id
        book.year = year
        book.price = price
        book.quantity = quantity
        book.available = available

        db.session.commit()
        flash(f"Cập nhật thông tin cuốn sách '{title}' thành công!", "success")
        return redirect(url_for("book_detail", id=book.id))

    return render_template("books/edit.html", book=book, categories=categories)


@app.route("/books/delete/<int:id>", methods=["POST"])
def delete_book(id):
    book = db.session.get(Book, id)
    if book:
        cat_id = book.category_id
        title = book.title
        db.session.delete(book)
        db.session.commit()
        flash(f"Đã xóa cuốn sách '{title}' khỏi cơ sở dữ liệu!", "success")
        return redirect(url_for("list_books", category_id=cat_id))
    else:
        flash("Sách không tồn tại!", "danger")
        return redirect(url_for("list_books"))


# ==========================================
# 6. RESTFUL API (JSON ENDPOINTS)
# ==========================================
@app.route("/api/dashboard/stats")
def api_stats():
    return jsonify({
        "total_categories": Category.query.count(),
        "total_books": Book.query.count(),
        "available_books": Book.query.filter_by(available=True).count(),
        "total_inventory_value": db.session.scalar(db.select(func.sum(Book.price * Book.quantity))) or 0.0
    })


@app.route("/api/categories")
def api_categories():
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories])


@app.route("/api/books")
def api_books():
    category_id = request.args.get("category_id", type=int)
    query = Book.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    books = query.all()
    return jsonify([b.to_dict() for b in books])


@app.route("/api/books/<int:id>")
def api_book_detail(id):
    book = db.session.get(Book, id)
    if not book:
        return jsonify({"error": f"Không có sách với ID = {id}"}), 404
    return jsonify(book.to_dict())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
