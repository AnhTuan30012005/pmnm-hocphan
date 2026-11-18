import os
import uuid
from datetime import datetime, timedelta
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, abort
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc, or_
from werkzeug.utils import secure_filename
from models import db, Category, Book, Order, OrderItem, OrderStatusHistory
from forms import CheckoutForm, BookForm, CategoryForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "nhasach-songhuong-secret-key-2026"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nhasach.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB tối đa
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
db.init_app(app)


# ==========================================
# JINJA2 FILTERS VÀ CONTEXT PROCESSOR
# ==========================================
@app.template_filter("vnd")
def vnd_filter(value):
    try:
        val = int(value)
        return f"{val:,}".replace(",", ".") + " đ"
    except (ValueError, TypeError):
        return "0 đ"


@app.context_processor
def inject_common_data():
    # 1. Tổng số lượng sách trong giỏ hàng (hiển thị trên badge cam)
    cart = session.get("cart", {})
    cart_count = sum(cart.values()) if cart else 0

    # 2. Số đơn hàng chờ xác nhận (hiển thị trên badge menu admin)
    try:
        pending_orders_count = Order.query.filter_by(status="Chờ xác nhận").count()
    except Exception:
        pending_orders_count = 0

    return {
        "cart_count": cart_count,
        "pending_orders_count": pending_orders_count,
        "now": datetime.now()
    }


# ==========================================
# GIỎ HÀNG (SESSION HELPERS)
# ==========================================
def get_cart():
    return session.get("cart", {})

def save_cart(cart):
    session["cart"] = cart
    session.modified = True

def get_cart_details():
    """
    Lấy chi tiết giỏ hàng:
    - Giá luôn lấy mới nhất từ CSDL (không lưu giá trong session)
    - Kiểm tra và tự động điều chỉnh số lượng nếu vượt quá tồn kho
    """
    cart = get_cart()
    items = []
    subtotal = 0
    updated_cart = {}

    for book_id_str, qty in list(cart.items()):
        try:
            b_id = int(book_id_str)
        except ValueError:
            continue

        book = db.session.get(Book, b_id)
        if not book:
            continue  # Sách đã bị xóa khỏi CSDL thì bỏ khỏi giỏ

        # Đảm bảo số lượng không vượt quá tồn kho
        actual_qty = min(qty, book.stock) if book.stock > 0 else 0
        if actual_qty > 0:
            updated_cart[str(b_id)] = actual_qty
            line_total = book.price * actual_qty
            subtotal += line_total
            items.append({
                "book": book,
                "quantity": actual_qty,
                "unit_price": book.price,
                "line_total": line_total,
                "is_max": actual_qty >= book.stock
            })

    save_cart(updated_cart)

    # Quy tắc phí giao hàng: 20.000 đ, miễn phí khi tạm tính từ 200.000 đ
    shipping_fee = 0 if subtotal >= 200000 or subtotal == 0 else 20000
    grand_total = subtotal + shipping_fee

    return {
        "items": items,
        "cart_items": items,
        "subtotal": subtotal,
        "shipping_fee": shipping_fee,
        "grand_total": grand_total,
        "item_count": len(items)
    }


# ==========================================
# PHẦN A. TRANG BÁN HÀNG
# ==========================================

# Màn hình ①: Danh sách sách
@app.route("/")
@app.route("/books")
def book_list():
    query_str = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", type=int)

    query = Book.query

    if query_str:
        query = query.filter(
            or_(Book.title.ilike(f"%{query_str}%"), Book.author.ilike(f"%{query_str}%"))
        )

    if category_id:
        query = query.filter(Book.category_id == category_id)

    books = query.order_by(Book.id.asc()).all()
    categories = Category.query.order_by(Category.name.asc()).all()

    return render_template(
        "books.html",
        books=books,
        categories=categories,
        selected_category_id=category_id,
        q=query_str
    )


# Màn hình ②: Chọn sách chi tiết
@app.route("/books/<int:id>")
def book_detail(id):
    book = db.session.get(Book, id)
    if not book:
        abort(404)

    cart = get_cart()
    in_cart_qty = cart.get(str(book.id), 0)
    max_can_add = max(0, book.stock - in_cart_qty)

    return render_template(
        "book_detail.html",
        book=book,
        in_cart_qty=in_cart_qty,
        max_can_add=max_can_add
    )


# Thêm vào giỏ hàng
@app.route("/cart/add/<int:book_id>", methods=["POST"])
def add_to_cart(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        abort(404)

    if book.stock <= 0:
        flash(f"Sách '{book.title}' hiện đã hết hàng!", "warning")
        return redirect(request.referrer or url_for("book_list"))

    # Số lượng muốn thêm (từ màn hình ① là 1, từ màn hình ② là ô số lượng)
    try:
        qty_to_add = int(request.form.get("quantity", 1))
        if qty_to_add < 1:
            qty_to_add = 1
    except ValueError:
        qty_to_add = 1

    cart = get_cart()
    current_in_cart = cart.get(str(book_id), 0)

    if current_in_cart + qty_to_add > book.stock:
        flash(
            f"Không thể thêm {qty_to_add} cuốn '{book.title}'. Tồn kho chỉ còn {book.stock} cuốn (bạn đã có {current_in_cart} trong giỏ).",
            "danger"
        )
        return redirect(request.referrer or url_for("book_detail", id=book_id))

    cart[str(book_id)] = current_in_cart + qty_to_add
    save_cart(cart)

    if qty_to_add == 1:
        flash(f"Đã thêm '{book.title}' vào giỏ hàng.", "success")
    else:
        flash(f"✓ Đã thêm {qty_to_add} × {book.title} vào giỏ hàng.", "success")

    return redirect(request.referrer or url_for("book_list"))


# Màn hình ③: Giỏ hàng
@app.route("/cart")
def view_cart():
    cart_data = get_cart_details()
    return render_template("cart.html", cart=cart_data)


# Cập nhật số lượng giỏ hàng (+, -, xóa) - PRG
@app.route("/cart/update/<int:book_id>/<action>", methods=["POST"])
def update_cart_item(book_id, action):
    cart = get_cart()
    key = str(book_id)

    if key in cart:
        book = db.session.get(Book, book_id)
        if not book:
            cart.pop(key, None)
        else:
            if action == "increase":
                if cart[key] < book.stock:
                    cart[key] += 1
                else:
                    flash(f"Đã đạt số lượng tồn kho tối đa ({book.stock} cuốn)!", "warning")
            elif action == "decrease":
                cart[key] -= 1
                if cart[key] <= 0:
                    cart.pop(key, None)
                    flash(f"Đã bỏ '{book.title}' khỏi giỏ hàng.", "info")
            elif action == "remove":
                cart.pop(key, None)
                flash(f"Đã xóa '{book.title}' khỏi giỏ hàng.", "info")

        save_cart(cart)

    return redirect(url_for("view_cart"))


# Xóa toàn bộ giỏ hàng
@app.route("/cart/clear", methods=["POST"])
def clear_cart():
    session.pop("cart", None)
    flash("Đã xóa toàn bộ giỏ hàng.", "info")
    return redirect(url_for("view_cart"))


# Màn hình ④: Thông tin khách hàng & Đặt hàng
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart_data = get_cart_details()
    if not cart_data["items"]:
        flash("Giỏ hàng của bạn đang trống! Vui lòng chọn sách trước khi đặt hàng.", "warning")
        return redirect(url_for("view_cart"))

    form = CheckoutForm()
    if form.validate_on_submit():
        # 1. Kiểm tra lại tồn kho CSDL ngay trước khi tạo đơn
        for item in cart_data["items"]:
            book = db.session.get(Book, item["book"].id)
            if not book or book.stock < item["quantity"]:
                flash(
                    f"Rất tiếc! Sách '{item['book'].title}' chỉ còn {book.stock if book else 0} cuốn trong kho, không đủ số lượng bạn yêu cầu.",
                    "danger"
                )
                return redirect(url_for("view_cart"))

        # 2. Tạo đơn hàng mới (trạng thái: Chờ xác nhận)
        new_order = Order(
            customer_name=form.customer_name.data.strip(),
            phone=form.phone.data.strip(),
            email=form.email.data.strip() if form.email.data else "",
            address=form.address.data.strip(),
            note=form.note.data.strip() if form.note.data else "",
            payment_method=form.payment_method.data,
            shipping_fee=cart_data["shipping_fee"],
            subtotal=cart_data["subtotal"],
            total_amount=cart_data["grand_total"],
            status="Chờ xác nhận"
        )
        db.session.add(new_order)
        db.session.flush()  # Cấp order.id trước khi thêm OrderItem

        # 3. Tạo các OrderItem, lưu đơn giá tại thời điểm đặt, trừ tồn kho
        for item in cart_data["items"]:
            order_item = OrderItem(
                order_id=new_order.id,
                book_id=item["book"].id,
                quantity=item["quantity"],
                unit_price=item["unit_price"]
            )
            db.session.add(order_item)

            # Trừ tồn kho
            book = db.session.get(Book, item["book"].id)
            book.stock -= item["quantity"]

        # 4. Ghi lịch sử trạng thái ban đầu
        history = OrderStatusHistory(
            order_id=new_order.id,
            status="Chờ xác nhận",
            note="Khách hàng đặt hàng thành công qua website"
        )
        db.session.add(history)

        db.session.commit()

        # 5. Xóa giỏ hàng trong session và chuyển sang màn hình ⑤
        session.pop("cart", None)
        flash(f"Đặt hàng thành công! Đơn hàng #{new_order.id} của bạn đang được xử lý.", "success")
        return redirect(url_for("order_success", id=new_order.id))

    return render_template("checkout.html", form=form, cart=cart_data)


# Màn hình ⑤: Đặt hàng thành công
@app.route("/orders/<int:id>")
def order_success(id):
    order = db.session.get(Order, id)
    if not order:
        abort(404)
    return render_template("order_success.html", order=order)


# ==========================================
# PHẦN B. TRANG QUẢN TRỊ (/admin)
# ==========================================

# Màn hình ⑥: Tổng quan Quản trị
@app.route("/admin")
@app.route("/admin/dashboard")
def admin_dashboard():
    # 4 thẻ thống kê
    total_books = db.session.scalar(db.select(func.count(Book.id))) or 0
    pending_orders = db.session.scalar(
        db.select(func.count(Order.id)).where(Order.status == "Chờ xác nhận")
    ) or 0

    # Doanh thu tháng hiện tại (các đơn 'Hoàn tất')
    now = datetime.now()
    first_day_of_month = datetime(now.year, now.month, 1)
    monthly_revenue = db.session.scalar(
        db.select(func.sum(Order.total_amount))
        .where(Order.status == "Hoàn tất")
        .where(Order.created_at >= first_day_of_month)
    ) or 0

    # Số sách sắp hết hàng (stock <= 5)
    low_stock_count = db.session.scalar(
        db.select(func.count(Book.id)).where(Book.stock <= 5)
    ) or 0

    # 5 đơn hàng mới nhất
    recent_orders = (
        Order.query.order_by(Order.id.desc()).limit(5).all()
    )

    # Danh sách sách sắp hết hàng (<= 5)
    low_stock_books = (
        Book.query.filter(Book.stock <= 5)
        .order_by(Book.stock.asc())
        .limit(10)
        .all()
    )

    # Doanh thu 7 ngày gần nhất (cho Chart.js)
    daily_labels = []
    daily_revenue = []
    for i in range(6, -1, -1):
        day_start = datetime(now.year, now.month, now.day) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        day_rev = db.session.scalar(
            db.select(func.sum(Order.total_amount))
            .where(Order.status == "Hoàn tất")
            .where(Order.created_at >= day_start)
            .where(Order.created_at < day_end)
        ) or 0
        daily_labels.append(day_start.strftime("%d/%m"))
        daily_revenue.append(day_rev)

    return render_template(
        "admin/dashboard.html",
        total_books=total_books,
        pending_orders=pending_orders,
        monthly_revenue=monthly_revenue,
        low_stock_count=low_stock_count,
        recent_orders=recent_orders,
        low_stock_books=low_stock_books,
        daily_labels=daily_labels,
        daily_revenue=daily_revenue,
        current_month=now.month
    )


# Màn hình ⑦: Quản lý sách
@app.route("/admin/books")
def admin_books():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", type=int)
    stock_filter = request.args.get("stock_filter", "all")

    query = Book.query

    if search:
        query = query.filter(
            or_(Book.title.ilike(f"%{search}%"), Book.author.ilike(f"%{search}%"))
        )

    if category_id:
        query = query.filter(Book.category_id == category_id)

    if stock_filter == "available":
        query = query.filter(Book.stock > 5)
    elif stock_filter == "low":
        query = query.filter(Book.stock > 0, Book.stock <= 5)
    elif stock_filter == "out":
        query = query.filter(Book.stock == 0)

    # 5 cuốn/trang, mới nhất trước
    pagination = query.order_by(Book.id.desc()).paginate(
        page=page, per_page=5, error_out=False
    )

    categories = Category.query.order_by(Category.name.asc()).all()

    # Kiểm tra xem mỗi cuốn sách có trong đơn hàng không (để cấm xóa)
    book_order_counts = dict(
        db.session.query(OrderItem.book_id, func.count(OrderItem.id))
        .group_by(OrderItem.book_id)
        .all()
    )

    return render_template(
        "admin/books.html",
        pagination=pagination,
        books=pagination.items,
        categories=categories,
        search=search,
        selected_category_id=category_id,
        stock_filter=stock_filter,
        book_order_counts=book_order_counts
    )


# Màn hình ⑧: Thêm sách mới
@app.route("/admin/books/new", methods=["GET", "POST"])
def admin_add_book():
    form = BookForm()
    categories = Category.query.order_by(Category.name.asc()).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        # Kiểm tra trùng tên sách (không phân biệt hoa thường)
        existing = Book.query.filter(
            func.lower(Book.title) == func.lower(form.title.data.strip())
        ).first()
        if existing:
            form.title.errors.append("Tên sách này đã tồn tại trong hệ thống!")
            return render_template("admin/book_form.html", form=form, is_edit=False)

        # Xử lý upload ảnh bìa
        image_filename = ""
        if form.image.data:
            file = form.image.data
            ext = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            file.save(file_path)
            image_filename = unique_filename

        new_book = Book(
            title=form.title.data.strip(),
            author=form.author.data.strip(),
            category_id=form.category_id.data,
            publisher=form.publisher.data.strip() if form.publisher.data else "NXB Đại học Huế",
            year=form.year.data,
            price=form.price.data,
            stock=form.stock.data,
            description=form.description.data.strip() if form.description.data else "",
            image=image_filename
        )
        db.session.add(new_book)
        db.session.commit()

        flash(f"Thêm sách '{new_book.title}' thành công!", "success")
        return redirect(url_for("admin_books"))

    return render_template("admin/book_form.html", form=form, is_edit=False)


# Màn hình ⑧: Sửa sách
@app.route("/admin/books/<int:id>/edit", methods=["GET", "POST"])
def admin_edit_book(id):
    book = db.session.get(Book, id)
    if not book:
        abort(404)

    form = BookForm(obj=book)
    categories = Category.query.order_by(Category.name.asc()).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        # Kiểm tra trùng tên sách (bỏ qua chính cuốn đang sửa)
        existing = Book.query.filter(
            func.lower(Book.title) == func.lower(form.title.data.strip()),
            Book.id != id
        ).first()
        if existing:
            form.title.errors.append("Tên sách này đã bị trùng với một cuốn khác!")
            return render_template("admin/book_form.html", form=form, is_edit=True, book=book)

        # Xử lý upload ảnh mới
        if form.image.data:
            file = form.image.data
            ext = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            file.save(file_path)

            # Xóa ảnh cũ nếu có
            if book.image:
                old_path = os.path.join(app.config["UPLOAD_FOLDER"], book.image)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except OSError:
                        pass

            book.image = unique_filename

        book.title = form.title.data.strip()
        book.author = form.author.data.strip()
        book.category_id = form.category_id.data
        book.publisher = form.publisher.data.strip() if form.publisher.data else "NXB Đại học Huế"
        book.year = form.year.data
        book.price = form.price.data
        book.stock = form.stock.data
        book.description = form.description.data.strip() if form.description.data else ""

        db.session.commit()
        flash(f"Cập nhật sách '{book.title}' thành công!", "success")
        return redirect(url_for("admin_books"))

    return render_template("admin/book_form.html", form=form, is_edit=True, book=book)


# Xóa sách (Chỉ xóa nếu sách chưa từng xuất hiện trong đơn hàng nào)
@app.route("/admin/books/<int:id>/delete", methods=["POST"])
def admin_delete_book(id):
    book = db.session.get(Book, id)
    if not book:
        abort(404)

    # Kiểm tra ràng buộc đơn hàng
    if len(book.order_items) > 0:
        flash(f"✕ Không thể xóa sách '{book.title}': sách này đã có trong đơn hàng!", "danger")
        return redirect(url_for("admin_books"))

    # Xóa file ảnh bìa nếu có
    if book.image:
        img_path = os.path.join(app.config["UPLOAD_FOLDER"], book.image)
        if os.path.exists(img_path):
            try:
                os.remove(img_path)
            except OSError:
                pass

    title = book.title
    db.session.delete(book)
    db.session.commit()
    flash(f"Đã xóa sách '{title}'.", "success")
    return redirect(url_for("admin_books"))


# Màn hình ⑨: Quản lý danh mục sách
@app.route("/admin/categories", methods=["GET", "POST"])
def admin_categories():
    form = CategoryForm()

    if form.validate_on_submit():
        name = form.name.data.strip()
        # Kiểm tra trùng tên (không phân biệt hoa thường)
        existing = Category.query.filter(
            func.lower(Category.name) == func.lower(name)
        ).first()
        if existing:
            form.name.errors.append("Danh mục này đã tồn tại.")
        else:
            new_cat = Category(name=name, description=form.description.data.strip() if form.description.data else "")
            db.session.add(new_cat)
            db.session.commit()
            flash(f"Thêm danh mục '{name}' thành công!", "success")
            return redirect(url_for("admin_categories"))

    # Truy vấn danh mục kèm số lượng sách bằng một truy vấn group_by
    cat_counts = (
        db.session.query(Category, func.count(Book.id).label("book_count"))
        .outerjoin(Book, Category.id == Book.category_id)
        .group_by(Category.id)
        .order_by(Category.id.asc())
        .all()
    )

    return render_template("admin/categories.html", cat_counts=cat_counts, form=form)


# Sửa danh mục sách
@app.route("/admin/categories/<int:id>/edit", methods=["POST"])
def admin_edit_category(id):
    cat = db.session.get(Category, id)
    if not cat:
        abort(404)

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()

    if not name:
        flash("Tên danh mục không được để trống!", "danger")
        return redirect(url_for("admin_categories"))

    existing = Category.query.filter(
        func.lower(Category.name) == func.lower(name),
        Category.id != id
    ).first()
    if existing:
        flash(f"Tên danh mục '{name}' đã tồn tại!", "warning")
        return redirect(url_for("admin_categories"))

    cat.name = name
    cat.description = description
    db.session.commit()
    flash(f"Cập nhật danh mục '{name}' thành công!", "success")
    return redirect(url_for("admin_categories"))


# Xóa danh mục sách (Chỉ xóa khi không còn sách nào)
@app.route("/admin/categories/<int:id>/delete", methods=["POST"])
def admin_delete_category(id):
    cat = db.session.get(Category, id)
    if not cat:
        abort(404)

    book_count = len(cat.books)
    if book_count > 0:
        flash(f"✕ Không thể xoá \"{cat.name}\": còn {book_count} sách.", "danger")
        return redirect(url_for("admin_categories"))

    cat_name = cat.name
    db.session.delete(cat)
    db.session.commit()
    flash(f"Đã xóa danh mục '{cat_name}'.", "success")
    return redirect(url_for("admin_categories"))


# Màn hình ⑩: Danh sách đơn hàng
@app.route("/admin/orders")
def admin_orders():
    page = request.args.get("page", 1, type=int)
    status_tab = request.args.get("status", "all")
    search = request.args.get("q", "").strip()

    # Thống kê số lượng đơn mỗi trạng thái bằng một truy vấn group_by
    status_group = dict(
        db.session.query(Order.status, func.count(Order.id))
        .group_by(Order.status)
        .all()
    )
    total_orders_count = sum(status_group.values())

    query = Order.query

    # Lọc theo tab trạng thái
    if status_tab != "all":
        query = query.filter(Order.status == status_tab)

    # Tìm kiếm theo mã đơn (#id), tên khách hàng, số điện thoại
    if search:
        search_id = None
        clean_search = search.replace("#", "").strip()
        if clean_search.isdigit():
            search_id = int(clean_search)

        if search_id is not None:
            query = query.filter(
                or_(
                    Order.id == search_id,
                    Order.customer_name.ilike(f"%{search}%"),
                    Order.phone.ilike(f"%{search}%")
                )
            )
        else:
            query = query.filter(
                or_(
                    Order.customer_name.ilike(f"%{search}%"),
                    Order.phone.ilike(f"%{search}%")
                )
            )

    # Tính tổng giá trị và số lượng đơn của bộ lọc hiện tại
    filtered_orders = query.all()
    current_filter_count = len(filtered_orders)
    current_filter_total_value = sum(o.total_amount for o in filtered_orders)

    # Phân trang: 10 đơn / trang, mới nhất trước
    pagination = query.order_by(Order.id.desc()).paginate(
        page=page, per_page=10, error_out=False
    )

    return render_template(
        "admin/orders.html",
        orders=pagination.items,
        pagination=pagination,
        status_tab=status_tab,
        search=search,
        status_group=status_group,
        total_orders_count=total_orders_count,
        current_filter_count=current_filter_count,
        current_filter_total_value=current_filter_total_value
    )


# Màn hình ⑪: Chi tiết đơn hàng & Xử lý trạng thái
@app.route("/admin/orders/<int:id>", methods=["GET", "POST"])
def admin_order_detail(id):
    order = db.session.get(Order, id)
    if not order:
        abort(404)

    if request.method == "POST":
        action = request.form.get("action")
        new_status = request.form.get("new_status")

        # Máy trạng thái hợp lệ
        # Chờ xác nhận -> Đang giao -> Hoàn tất
        # Chờ xác nhận, Đang giao -> Đã huỷ
        # Hoàn tất, Đã huỷ: không đổi được nữa
        if order.status in ["Hoàn tất", "Đã huỷ"]:
            flash(f"Đơn hàng đã ở trạng thái '{order.status}', không thể thay đổi nữa!", "warning")
            return redirect(url_for("admin_order_detail", id=id))

        if action == "cancel":
            # Hủy đơn hàng: hoàn lại tồn kho các sách trong đơn
            for item in order.items:
                book = db.session.get(Book, item.book_id)
                if book:
                    book.stock += item.quantity

            order.status = "Đã huỷ"
            history = OrderStatusHistory(
                order_id=order.id,
                status="Đã huỷ",
                note="Quản trị viên hủy đơn hàng (đã hoàn lại tồn kho)"
            )
            db.session.add(history)
            db.session.commit()
            flash(f"Đã hủy đơn hàng #{order.id} và hoàn lại tồn kho thành công!", "success")
            return redirect(url_for("admin_order_detail", id=id))

        elif (action == "update_status" or new_status) and new_status:
            note = request.form.get("note", "").strip()
            valid_transition = False
            if order.status == "Chờ xác nhận" and new_status in ["Đang giao", "Đã huỷ"]:
                valid_transition = True
            elif order.status == "Đang giao" and new_status in ["Hoàn tất", "Đã huỷ"]:
                valid_transition = True

            if not valid_transition:
                flash(f"Không thể chuyển trạng thái từ '{order.status}' sang '{new_status}'!", "danger")
                return redirect(url_for("admin_order_detail", id=id))

            if new_status == "Đã huỷ":
                # Hoàn tồn kho
                for item in order.items:
                    book = db.session.get(Book, item.book_id)
                    if book:
                        book.stock += item.quantity

            order.status = new_status
            history = OrderStatusHistory(
                order_id=order.id,
                status=new_status,
                note=note if note else f"Chuyển trạng thái sang '{new_status}'"
            )
            db.session.add(history)
            db.session.commit()
            flash(f"Đã cập nhật trạng thái đơn hàng #{order.id} sang '{new_status}'!", "success")
            return redirect(url_for("admin_order_detail", id=id))

    return render_template("admin/order_detail.html", order=order)


# ==========================================
# SEED DATA BAN ĐẦU (ĐÚNG THEO SLIDE)
# ==========================================
def init_db():
    with app.app_context():
        db.create_all()
        if Category.query.count() == 0:
            # 6 danh mục như trên slide trang 12
            c_laptrinh = Category(name="Lập trình", description="Sách phát triển phần mềm, ngôn ngữ lập trình")
            c_csdl = Category(name="Cơ sở dữ liệu", description="Hệ quản trị CSDL quan hệ, NoSQL, tối ưu hóa truy vấn")
            c_congcu = Category(name="Công cụ", description="Git, Docker, Linux và các công cụ DevOps")
            c_mang = Category(name="Mạng", description="Mạng máy tính, giao thức và an toàn thông tin")
            c_kynang = Category(name="Kỹ năng lập trình", description="Kiến trúc code sạch, refactoring, tư duy thiết kế")
            c_thietke = Category(name="Thiết kế", description="UI/UX và thiết kế hệ thống")

            db.session.add_all([c_laptrinh, c_csdl, c_congcu, c_mang, c_kynang, c_thietke])
            db.session.commit()

            # 6 cuốn sách như trên slide trang 4 và 10
            b1 = Book(title="Lập trình Python cơ bản", author="Nguyễn Văn A", publisher="NXB Đại học Huế", year=2024, price=95000, stock=30, description="Giáo trình lập trình Python căn bản cho sinh viên khoa CNTT.", category_id=c_laptrinh.id)
            b2 = Book(title="Giáo trình Flask", author="Miguel Grinberg", publisher="NXB Đại học Huế", year=2024, price=120000, stock=20, description="Xây dựng ứng dụng web hiện đại với Python Flask và Jinja2.", category_id=c_laptrinh.id)
            b3 = Book(title="Cơ sở dữ liệu", author="Trần Văn B", publisher="NXB Đại học Huế", year=2023, price=85000, stock=0, description="Lý thuyết và thực hành thiết kế CSDL quan hệ chuẩn hóa.", category_id=c_csdl.id)
            b4 = Book(title="Pro Git", author="Scott Chacon", publisher="NXB Đại học Huế", year=2022, price=150000, stock=15, description="Hướng dẫn toàn diện về kiểm soát phiên bản mã nguồn với Git.", category_id=c_congcu.id)
            b5 = Book(title="Mạng máy tính", author="Lê Văn C", publisher="NXB Đại học Huế", year=2023, price=110000, stock=12, description="Kiến trúc mạng TCP/IP, định tuyến và phân tầng mạng.", category_id=c_mang.id)
            b6 = Book(title="Clean Code", author="Robert C. Martin", publisher="NXB Đại học Huế", year=2020, price=180000, stock=5, description="Nghệ thuật viết mã nguồn sạch, dễ đọc và dễ bảo trì.", category_id=c_kynang.id)

            db.session.add_all([b1, b2, b3, b4, b5, b6])
            db.session.commit()

            # Các đơn hàng mẫu như trên slide trang 9 và 13
            # Đơn #12: Nguyễn Văn An, 460.000 đ, Chờ xác nhận
            o12 = Order(
                id=12,
                customer_name="Nguyễn Văn An",
                phone="0912345678",
                email="an.nguyen@example.com",
                address="12 Lê Lợi, phường Thuận Hoá, Huế",
                note="Giao giờ hành chính",
                payment_method="Tiền mặt khi nhận hàng",
                subtotal=460000,
                shipping_fee=0,
                total_amount=460000,
                status="Chờ xác nhận",
                created_at=datetime.now() - timedelta(days=1, hours=2)
            )
            # Đơn #11: Trần Thị Bình, 215.000 đ, Đang giao
            o11 = Order(
                id=11,
                customer_name="Trần Thị Bình",
                phone="0987654321",
                email="binh.tran@example.com",
                address="45 Hùng Vương, Huế",
                note="Gọi trước khi giao",
                payment_method="Tiền mặt khi nhận hàng",
                subtotal=195000,
                shipping_fee=20000,
                total_amount=215000,
                status="Đang giao",
                created_at=datetime.now() - timedelta(days=2)
            )
            # Đơn #10: Lê Hoàng Cường, 180.000 đ, Hoàn tất
            o10 = Order(
                id=10,
                customer_name="Lê Hoàng Cường",
                phone="0901234567",
                email="cuong.le@example.com",
                address="77 Nguyễn Huệ, Huế",
                note="",
                payment_method="Chuyển khoản",
                subtotal=180000,
                shipping_fee=20000,
                total_amount=200000,
                status="Hoàn tất",
                created_at=datetime.now() - timedelta(days=3)
            )
            # Đơn #9: Phạm Minh Dũng, 95.000 đ, Đã huỷ
            o9 = Order(
                id=9,
                customer_name="Phạm Minh Dũng",
                phone="0933445566",
                email="dung.pham@example.com",
                address="88 Bà Triệu, Huế",
                note="Đổi ý không mua nữa",
                payment_method="Tiền mặt khi nhận hàng",
                subtotal=95000,
                shipping_fee=20000,
                total_amount=115000,
                status="Đã huỷ",
                created_at=datetime.now() - timedelta(days=4)
            )
            # Đơn #8: Hoàng Thu Hà, 300.000 đ, Chờ xác nhận
            o8 = Order(
                id=8,
                customer_name="Hoàng Thu Hà",
                phone="0987654321",
                email="ha.hoang@example.com",
                address="102 Bến Nghé, Huế",
                note="",
                payment_method="Chuyển khoản",
                subtotal=300000,
                shipping_fee=0,
                total_amount=300000,
                status="Chờ xác nhận",
                created_at=datetime.now() - timedelta(days=5)
            )
            # Đơn #5: Võ Quốc Khánh, 215.000 đ, Chờ xác nhận
            o5 = Order(
                id=5,
                customer_name="Võ Quốc Khánh",
                phone="0901234567",
                email="khanh.vo@example.com",
                address="15 Hà Nội, Huế",
                note="",
                payment_method="Tiền mặt khi nhận hàng",
                subtotal=195000,
                shipping_fee=20000,
                total_amount=215000,
                status="Chờ xác nhận",
                created_at=datetime.now() - timedelta(days=6)
            )

            db.session.add_all([o12, o11, o10, o9, o8, o5])
            db.session.commit()

            # Các OrderItem cho đơn #12
            db.session.add_all([
                OrderItem(order_id=o12.id, book_id=b1.id, quantity=2, unit_price=95000),
                OrderItem(order_id=o12.id, book_id=b2.id, quantity=1, unit_price=120000),
                OrderItem(order_id=o12.id, book_id=b4.id, quantity=1, unit_price=150000),
            ])
            # Trừ tồn kho tương ứng của đơn #12 như trong slide trang 10 (Python 30 -> 28, Flask 20 -> 19, Pro Git 15 -> 14)
            b1.stock = 28
            b2.stock = 19
            b4.stock = 14

            # Lịch sử trạng thái cho đơn #12
            db.session.add(OrderStatusHistory(order_id=o12.id, status="Chờ xác nhận", note="Khách hàng đặt hàng"))
            db.session.add(OrderStatusHistory(order_id=o11.id, status="Chờ xác nhận", note="Khách hàng đặt hàng"))
            db.session.add(OrderStatusHistory(order_id=o11.id, status="Đang giao", note="Bàn giao đơn vị vận chuyển"))
            db.session.add(OrderStatusHistory(order_id=o10.id, status="Hoàn tất", note="Khách hàng đã nhận sách"))

            db.session.commit()
            print("-> Đã khởi tạo CSDL Nhà sách Sông Hương với dữ liệu mẫu chuẩn theo slide!")

init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
