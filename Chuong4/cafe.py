import math
from datetime import datetime
from flask import Flask, render_template, request, abort

app = Flask(__name__)

SHOP = {
    "name": "Cà phê Sông Hương",
    "address": "12 Lê Lợi, Huế",
    "phone": "0234 3888 999",
    "open": 7,
    "close": 22
}

PROMOTIONS = [
    "Giảm 10% cho sinh viên",
    "Mua 1 tặng 1 vào thứ Hai"
]

# Dữ liệu 7 món đúng theo thứ tự phân trang trong slide Bài 4:
# Trang 1: Cà phê đen, Cà phê sữa, Bạc xỉu
# Trang 2: Trà đào, Trà sữa, Nước cam
# Trang 3: Sinh tố bơ
MENU = [
    {"id": 1, "name": "cà phê đen", "price": 20000, "image": "ca-phe-den.jpg", "available": True},
    {"id": 2, "name": "cà phê sữa", "price": 25000, "image": "ca-phe-sua.jpg", "available": True},
    {"id": 3, "name": "bạc xỉu", "price": 30000, "image": "bac-xiu.jpg", "available": False},
    {"id": 4, "name": "trà đào", "price": 35000, "image": "tra-dao.jpg", "available": True},
    {"id": 5, "name": "trà sữa", "price": 30000, "image": "tra-sua.jpg", "available": True},
    {"id": 6, "name": "nước cam", "price": 35000, "image": "nuoc-cam.jpg", "available": True},
    {"id": 7, "name": "sinh tố bơ", "price": 40000, "image": "sinh-to-bo.jpg", "available": True},
]

PER_PAGE = 3  # Mỗi trang hiển thị 3 món


# Filter tự viết: 20000 -> 20.000 đ
@app.template_filter("vnd")
def vnd_filter(value):
    return f"{int(value):,}".replace(",", ".") + " đ"


# Trang chủ (/)
@app.get("/")
def index():
    hour = request.args.get("gio", type=int)
    if hour is None:
        hour = datetime.now().hour

    is_open = SHOP["open"] <= hour < SHOP["close"]

    return render_template(
        "index.html",
        shop=SHOP,
        hour=hour,
        is_open=is_open,
        promotions=PROMOTIONS
    )


# Thực đơn có phân trang (/menu?page=N)
@app.get("/menu")
def show_menu():
    # 1. Tính tổng số trang (7 món / 3 = 3 trang)
    total_items = len(MENU)
    pages = math.ceil(total_items / PER_PAGE) if total_items > 0 else 1

    # 2. Đọc tham số page từ URL
    page_str = request.args.get("page", "1")
    try:
        page = int(page_str)
    except ValueError:
        # Nếu ?page=abc không phải số, mặc định hiển thị như trang 1
        page = 1

    # 3. Nếu số trang < 1 hoặc vượt quá số trang tối đa -> trả về lỗi 404
    if page < 1 or page > pages:
        abort(404)

    # 4. Cắt danh sách món cho trang hiện tại (3 món / trang)
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    current_items = MENU[start:end]

    return render_template(
        "menu.html",
        shop=SHOP,
        items=current_items,
        page=page,
        pages=pages
    )


# Trang liên hệ (/contact)
@app.get("/contact")
def contact():
    return render_template("contact.html", shop=SHOP)


# Trang lỗi 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", shop=SHOP), 404


if __name__ == "__main__":
    app.run(debug=True)