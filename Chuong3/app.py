from flask import Flask, request, jsonify, abort, url_for
from markupsafe import escape

app = Flask(__name__)

# 1. List BOOKS >= 4 cuốn: id, title, author, year, category, available
BOOKS = [
    {
        "id": 1,
        "title": "Lập trình Python căn bản",
        "author": "Nguyễn Văn A",
        "year": 2021,
        "category": "Lập trình",
        "available": True,
    },
    {
        "id": 2,
        "title": "Lập trình Web với Flask",
        "author": "Trần Thị B",
        "year": 2022,
        "category": "Lập trình",
        "available": False,
    },
    {
        "id": 3,
        "title": "Cơ sở dữ liệu nâng cao",
        "author": "Lê Văn C",
        "year": 2020,
        "category": "Cơ sở dữ liệu",
        "available": True,
    },
    {
        "id": 4,
        "title": "Mạng máy tính cơ bản",
        "author": "Phạm Văn D",
        "year": 2023,
        "category": "Mạng máy tính",
        "available": True,
    },
]


def find_book(book_id):
    """Tìm sách theo id."""
    for book in BOOKS:
        if book["id"] == book_id:
            return book
    return None


def menu_chung():
    """Hàm tạo menu chung dùng lại cho các trang, tránh lặp mã nguồn."""
    return f"""
    <nav>
        <a href="{url_for('index')}">Trang chủ</a> |
        <a href="{url_for('books')}">Danh sách sách</a> |
        <a href="{url_for('api_books')}">API Sách</a>
    </nav>
    <hr>
    """


# 2. / : tổng số đầu sách, số sách sẵn sàng cho mượn
@app.route("/")
def index():
    tong_dau_sach = len(BOOKS)
    san_sang = sum(1 for b in BOOKS if b["available"])

    html = f"""
    {menu_chung()}
    <h1>Trang chủ thư viện (LibraryMS v0.1)</h1>
    <p>Tổng số đầu sách: <b>{escape(str(tong_dau_sach))}</b></p>
    <p>Số sách sẵn sàng cho mượn: <b>{escape(str(san_sang))}</b></p>
    <p><a href="{url_for('books')}">Xem danh sách sách</a></p>
    """
    return html


# 3. /books : bảng sách, tên sách liên kết đến chi tiết; lọc ?category=... kèm thanh liên kết
@app.route("/books")
def books():
    category_filter = request.args.get("category")

    # Tạo thanh liên kết lọc theo thể loại
    categories = sorted(list({b["category"] for b in BOOKS}))
    cat_links = [f'<a href="{url_for("books")}">Tất cả</a>']
    for cat in categories:
        cat_links.append(f'<a href="{url_for("books", category=cat)}">{escape(cat)}</a>')
    thanh_the_loai = " | ".join(cat_links)

    # Lọc danh sách nếu có category
    if category_filter:
        sach_hien_thi = [b for b in BOOKS if b["category"] == category_filter]
    else:
        sach_hien_thi = BOOKS

    # Tạo các dòng cho bảng sách
    rows = ""
    for b in sach_hien_thi:
        trang_thai = "Có sẵn" if b["available"] else "Đã mượn"
        detail_url = url_for("book_detail", book_id=b["id"])
        rows += f"""
        <tr>
            <td>{escape(str(b['id']))}</td>
            <td><a href="{detail_url}">{escape(b['title'])}</a></td>
            <td>{escape(b['author'])}</td>
            <td>{escape(str(b['year']))}</td>
            <td>{escape(b['category'])}</td>
            <td>{escape(trang_thai)}</td>
        </tr>
        """

    html = f"""
    {menu_chung()}
    <h1>Danh mục sách</h1>
    <p><b>Lọc theo thể loại:</b> {thanh_the_loai}</p>
    <table border="1" cellpadding="6" cellspacing="0">
        <thead>
            <tr>
                <th>ID</th>
                <th>Tên sách</th>
                <th>Tác giả</th>
                <th>Năm</th>
                <th>Thể loại</th>
                <th>Trạng thái</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """
    return html


# 4. /books/<int:book_id> : chi tiết; không tồn tại -> 404 "Không có sách với ID = ..."
@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = find_book(book_id)
    if not book:
        abort(404, description=f"Không có sách với ID = {book_id}")

    trang_thai = "Sẵn sàng cho mượn" if book["available"] else "Đang được mượn"
    html = f"""
    {menu_chung()}
    <h1>Chi tiết sách</h1>
    <p><b>ID:</b> {escape(str(book['id']))}</p>
    <p><b>Tên sách:</b> {escape(book['title'])}</p>
    <p><b>Tác giả:</b> {escape(book['author'])}</p>
    <p><b>Năm xuất bản:</b> {escape(str(book['year']))}</p>
    <p><b>Thể loại:</b> {escape(book['category'])}</p>
    <p><b>Trạng thái:</b> {escape(trang_thai)}</p>
    <p><a href="{url_for('books')}">← Quay lại danh sách sách</a></p>
    """
    return html


# 5. /api/books : JSON danh sách sách
@app.route("/api/books")
def api_books():
    category_filter = request.args.get("category")
    if category_filter:
        sach_hien_thi = [b for b in BOOKS if b["category"] == category_filter]
    else:
        sach_hien_thi = BOOKS
    return jsonify(sach_hien_thi)


# 5. /api/books/<int:book_id> : JSON; không tồn tại -> {"error": "..."} với mã 404
@app.route("/api/books/<int:book_id>")
def api_book_detail(book_id):
    book = find_book(book_id)
    if not book:
        return jsonify({"error": f"Không có sách với ID = {book_id}"}), 404
    return jsonify(book)


# 6. Trang 404 tuỳ biến, có menu chung (phân biệt HTML và API)
@app.errorhandler(404)
def page_not_found(e):
    message = getattr(e, "description", "Không tìm thấy trang yêu cầu")

    # Nếu gọi API thì trả về JSON lỗi 404
    if request.path.startswith("/api/"):
        return jsonify({"error": message}), 404

    # HTML trả về trang 404 tuỳ biến có menu chung
    html = f"""
    {menu_chung()}
    <h1>404 - Không tìm thấy trang</h1>
    <p>{escape(message)}</p>
    <p><a href="{url_for('books')}">Quay lại danh mục sách</a></p>
    """
    return html, 404


if __name__ == "__main__":
    app.run(debug=True)
