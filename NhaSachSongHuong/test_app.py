import os
import unittest
from datetime import datetime

# Đặt biến môi trường và file db test trước
TEST_DB = "test_nhasach.db"
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

from app import app, db
from models import Category, Book, Order, OrderItem, OrderStatusHistory


class NhaSachSongHuongTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{TEST_DB}"
        cls.client = app.test_client()

        with app.app_context():
            db.drop_all()
            db.create_all()

            # Khởi tạo dữ liệu mẫu chuẩn theo slide
            c1 = Category(name="Lập trình", description="Sách phát triển phần mềm, Python, Flask")
            c2 = Category(name="Cơ sở dữ liệu", description="SQL, SQLite, PostgreSQL")
            c3 = Category(name="Công cụ", description="Git, Docker, Linux")
            c_empty = Category(name="Danh mục rỗng", description="Chưa có sách nào")
            db.session.add_all([c1, c2, c3, c_empty])
            db.session.commit()

            # 4 cuốn sách mẫu
            b1 = Book(title="Lập trình Python cơ bản", author="Nguyễn Văn A", publisher="NXB Đại học Huế", year=2024, price=95000, stock=30, description="Giáo trình Python cơ bản", category_id=c1.id)
            b2 = Book(title="Giáo trình Flask", author="Miguel Grinberg", publisher="NXB Đại học Huế", year=2024, price=120000, stock=20, description="Web Flask hiện đại", category_id=c1.id)
            b3 = Book(title="Cơ sở dữ liệu", author="Trần Văn B", publisher="NXB Đại học Huế", year=2023, price=85000, stock=0, description="CSDL quan hệ", category_id=c2.id)
            b_isolated = Book(title="Sách chưa từng được đặt", author="Tác giả X", publisher="NXB Trẻ", year=2022, price=50000, stock=5, description="Sách dùng để test xóa", category_id=c3.id)
            db.session.add_all([b1, b2, b3, b_isolated])
            db.session.commit()

            # Đơn hàng mẫu #12
            o12 = Order(
                id=12,
                customer_name="Nguyễn Văn An",
                phone="0912345678",
                email="an.nguyen@example.com",
                address="77 Nguyễn Huệ, TP Huế",
                note="Giao vào buổi sáng",
                payment_method="Tiền mặt khi nhận hàng",
                subtotal=310000,
                shipping_fee=0,
                total_amount=310000,
                status="Chờ xác nhận"
            )
            db.session.add(o12)
            db.session.commit()

            # Chi tiết đơn hàng #12 gắn với b1
            item = OrderItem(order_id=o12.id, book_id=b1.id, quantity=2, unit_price=95000)
            db.session.add(item)
            db.session.add(OrderStatusHistory(order_id=o12.id, status="Chờ xác nhận", note="Khách hàng đặt hàng"))
            db.session.commit()

            cls.c1_id = c1.id
            cls.c_empty_id = c_empty.id
            cls.b1_id = b1.id
            cls.b2_id = b2.id
            cls.b3_id = b3.id
            cls.b_isolated_id = b_isolated.id
            cls.o12_id = o12.id

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.session.remove()
            db.drop_all()
        if os.path.exists(TEST_DB):
            try:
                os.remove(TEST_DB)
            except Exception:
                pass

    # ==========================================
    # PHẦN A: BÁN HÀNG & GIỎ HÀNG (SCREENS ① - ⑤)
    # ==========================================

    def test_01_catalog_view_and_filter(self):
        """Màn hình ①: Danh mục sách, lọc danh mục, tìm kiếm và badge giỏ hàng"""
        # Xem toàn bộ sách
        res = self.client.get("/books")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Lập trình Python cơ bản".encode("utf-8"), res.data)
        self.assertIn("Giáo trình Flask".encode("utf-8"), res.data)

        # Lọc theo danh mục Lập trình
        res_cat = self.client.get(f"/books?category={self.c1_id}")
        self.assertEqual(res_cat.status_code, 200)
        self.assertIn("Lập trình Python cơ bản".encode("utf-8"), res_cat.data)

        # Tìm kiếm theo từ khóa
        res_search = self.client.get("/books?q=Flask")
        self.assertEqual(res_search.status_code, 200)
        self.assertIn("Giáo trình Flask".encode("utf-8"), res_search.data)
        self.assertNotIn("Pro Git".encode("utf-8"), res_search.data)

    def test_02_book_detail_and_stock_badge(self):
        """Màn hình ②: Chi tiết sách & giới hạn số lượng theo tồn kho"""
        # Sách còn hàng (b1)
        res = self.client.get(f"/books/{self.b1_id}")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Lập trình Python cơ bản".encode("utf-8"), res.data)
        self.assertIn("Nguyễn Văn A".encode("utf-8"), res.data)

        # Sách hết hàng (b3: stock = 0)
        res_b3 = self.client.get(f"/books/{self.b3_id}")
        self.assertEqual(res_b3.status_code, 200)
        self.assertIn("Hết hàng".encode("utf-8"), res_b3.data)

    def test_03_cart_operations(self):
        """Màn hình ③: Thêm giỏ hàng, cập nhật tăng/giảm, xóa và tính tổng tiền"""
        # 1. Thêm 2 cuốn b1 vào giỏ
        res = self.client.post(f"/cart/add/{self.b1_id}", data={"quantity": 2}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Đã thêm 2".encode("utf-8"), res.data)

        # 2. Xem trang giỏ hàng
        res_cart = self.client.get("/cart")
        self.assertEqual(res_cart.status_code, 200)
        self.assertIn("Lập trình Python cơ bản".encode("utf-8"), res_cart.data)

        # 3. Tăng số lượng (+1)
        res_inc = self.client.post(f"/cart/update/{self.b1_id}/increase", follow_redirects=True)
        self.assertEqual(res_inc.status_code, 200)

        # 4. Giảm số lượng (-1)
        res_dec = self.client.post(f"/cart/update/{self.b1_id}/decrease", follow_redirects=True)
        self.assertEqual(res_dec.status_code, 200)

        # 5. Xóa 1 cuốn khỏi giỏ (action = remove)
        res_remove = self.client.post(f"/cart/update/{self.b1_id}/remove", follow_redirects=True)
        self.assertEqual(res_remove.status_code, 200)
        self.assertIn("Đã xóa".encode("utf-8"), res_remove.data)

        # 6. Thêm lại và xóa toàn bộ giỏ (Clear Cart)
        self.client.post(f"/cart/add/{self.b2_id}", data={"quantity": 1}, follow_redirects=True)
        res_clear = self.client.post("/cart/clear", follow_redirects=True)
        self.assertEqual(res_clear.status_code, 200)
        self.assertIn("Giỏ hàng của bạn đang trống".encode("utf-8"), res_clear.data)

    def test_04_checkout_and_order_creation(self):
        """Màn hình ④ & ⑤: Đặt hàng thành công, trừ tồn kho và phí vận chuyển"""
        # Làm trống giỏ trước khi test quy trình đặt hàng
        self.client.post("/cart/clear")

        # Thêm 2 cuốn b2 (120k * 2 = 240k >= 200k -> Phí ship = 0)
        self.client.post(f"/cart/add/{self.b2_id}", data={"quantity": 2}, follow_redirects=True)

        # Kiểm tra trang checkout hiển thị thông tin
        res_checkout = self.client.get("/checkout")
        self.assertEqual(res_checkout.status_code, 200)
        self.assertIn("Miễn phí".encode("utf-8"), res_checkout.data)

        # Gửi form đặt hàng
        checkout_payload = {
            "customer_name": "Trần Thị Lan",
            "phone": "0912345678",
            "email": "lan@example.com",
            "address": "123 Hùng Vương, TP Huế",
            "payment_method": "Tiền mặt khi nhận hàng",
            "note": "Gọi trước khi giao 15 phút"
        }
        res_post = self.client.post("/checkout", data=checkout_payload, follow_redirects=True)
        self.assertEqual(res_post.status_code, 200)
        self.assertIn("Đặt hàng thành công".encode("utf-8"), res_post.data)

        with app.app_context():
            # Kiểm tra tồn kho của b2 đã bị trừ 2 cuốn (từ 20 xuống 18)
            b2 = db.session.get(Book, self.b2_id)
            self.assertEqual(b2.stock, 18)

            # Kiểm tra đơn hàng mới được tạo
            order = Order.query.filter_by(customer_name="Trần Thị Lan").first()
            self.assertIsNotNone(order)
            self.assertEqual(order.shipping_fee, 0)
            self.assertEqual(order.total_amount, 240000)
            self.assertEqual(order.status, "Chờ xác nhận")
            self.assertEqual(len(order.items), 1)

    # ==========================================
    # PHẦN B: QUẢN TRỊ ADMIN (SCREENS ⑥ - ⑪)
    # ==========================================

    def test_05_admin_dashboard(self):
        """Màn hình ⑥: Tổng quan quản trị, 4 thẻ thống kê và biểu đồ"""
        res = self.client.get("/admin")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Tổng quan hệ thống".encode("utf-8"), res.data)
        self.assertIn("Đầu sách".encode("utf-8"), res.data)
        self.assertIn("Chờ xác nhận".encode("utf-8"), res.data)
        self.assertIn("revenueChart".encode("utf-8"), res.data)

    def test_06_admin_books_crud_and_safety_rule(self):
        """Màn hình ⑦ & ⑧: Quản lý sách, thêm sách mới, kiểm tra ràng buộc xóa"""
        # 1. Thêm sách mới
        new_book_data = {
            "title": "Clean Architecture Tiếng Việt",
            "author": "Robert C. Martin",
            "publisher": "NXB Đại học Huế",
            "year": 2024,
            "price": 175000,
            "stock": 10,
            "category_id": self.c1_id,
            "description": "Kiến trúc phần mềm sạch"
        }
        res_add = self.client.post("/admin/books/new", data=new_book_data, follow_redirects=True)
        self.assertEqual(res_add.status_code, 200)
        self.assertIn("thành công".encode("utf-8"), res_add.data)

        # 2. Chặn thêm sách trùng tên
        res_dup = self.client.post("/admin/books/new", data=new_book_data, follow_redirects=True)
        self.assertIn("Tên sách này đã tồn tại".encode("utf-8"), res_dup.data)

        # 3. Chặn xóa sách đã có trong đơn hàng (b1 có trong đơn o12)
        res_del_b1 = self.client.post(f"/admin/books/{self.b1_id}/delete", follow_redirects=True)
        self.assertIn("Không thể xóa sách".encode("utf-8"), res_del_b1.data)
        with app.app_context():
            self.assertIsNotNone(db.session.get(Book, self.b1_id))

        # 4. Xóa sách chưa từng có trong đơn hàng (b_isolated) -> thành công
        res_del_iso = self.client.post(f"/admin/books/{self.b_isolated_id}/delete", follow_redirects=True)
        self.assertIn("Đã xóa sách".encode("utf-8"), res_del_iso.data)
        with app.app_context():
            self.assertIsNone(db.session.get(Book, self.b_isolated_id))

    def test_07_admin_categories_and_safety_rule(self):
        """Màn hình ⑨: Quản lý danh mục, chặn xóa nếu còn sách"""
        # 1. Chặn xóa danh mục c1 vì c1 đang có sách
        res_del_c1 = self.client.post(f"/admin/categories/{self.c1_id}/delete", follow_redirects=True)
        self.assertIn("Không thể xoá".encode("utf-8"), res_del_c1.data)
        with app.app_context():
            self.assertIsNotNone(db.session.get(Category, self.c1_id))

        # 2. Xóa danh mục rỗng (c_empty không có sách) -> thành công
        res_del_empty = self.client.post(f"/admin/categories/{self.c_empty_id}/delete", follow_redirects=True)
        self.assertIn("Đã xóa danh mục".encode("utf-8"), res_del_empty.data)
        with app.app_context():
            self.assertIsNone(db.session.get(Category, self.c_empty_id))

    def test_08_admin_orders_and_state_machine(self):
        """Màn hình ⑩ & ⑪: Danh sách đơn hàng, chuyển trạng thái và hoàn kho khi hủy"""
        # 1. Xem danh sách đơn hàng
        res_orders = self.client.get("/admin/orders")
        self.assertEqual(res_orders.status_code, 200)
        self.assertIn("Nguyễn Văn An".encode("utf-8"), res_orders.data)

        # 2. Xem chi tiết đơn #12
        res_detail = self.client.get(f"/admin/orders/{self.o12_id}")
        self.assertEqual(res_detail.status_code, 200)
        self.assertIn("Chi tiết đơn hàng #12".encode("utf-8"), res_detail.data)

        # 3. Chuyển trạng thái: 'Chờ xác nhận' -> 'Đang giao'
        res_ship = self.client.post(
            f"/admin/orders/{self.o12_id}",
            data={"action": "update_status", "new_status": "Đang giao", "note": "Giao cho Viettel Post"},
            follow_redirects=True
        )
        self.assertEqual(res_ship.status_code, 200)
        self.assertIn("Đã cập nhật trạng thái đơn hàng".encode("utf-8"), res_ship.data)

        with app.app_context():
            order = db.session.get(Order, self.o12_id)
            self.assertEqual(order.status, "Đang giao")
            b1 = db.session.get(Book, self.b1_id)
            stock_before_cancel = b1.stock

        # 4. Chuyển trạng thái: 'Đang giao' -> 'Đã huỷ' (Phải hoàn trả tồn kho +2 cuốn cho b1)
        res_cancel = self.client.post(
            f"/admin/orders/{self.o12_id}",
            data={"action": "update_status", "new_status": "Đã huỷ", "note": "Khách báo hoãn không nhận"},
            follow_redirects=True
        )
        self.assertEqual(res_cancel.status_code, 200)

        with app.app_context():
            order = db.session.get(Order, self.o12_id)
            self.assertEqual(order.status, "Đã huỷ")
            # Tồn kho b1 phải được hoàn đúng +2 cuốn
            b1 = db.session.get(Book, self.b1_id)
            self.assertEqual(b1.stock, stock_before_cancel + 2)

            # Đơn đã ở trạng thái cuối cùng ('Đã huỷ') -> Không cho phép đổi nữa
            res_locked = self.client.post(
                f"/admin/orders/{self.o12_id}",
                data={"new_status": "Hoàn tất"},
                follow_redirects=True
            )
            self.assertIn("không thể thay đổi nữa".encode("utf-8"), res_locked.data)

    def test_09_checkout_phone_validation_regex(self):
        """Màn hình ④: Bắt lỗi số điện thoại không hợp lệ theo regex ^0\\d{9}$"""
        self.client.post("/cart/clear")
        self.client.post(f"/cart/add/{self.b1_id}", data={"quantity": 1}, follow_redirects=True)

        invalid_data = {
            "customer_name": "Nguyễn Văn Test",
            "phone": "0987654",  # Không đủ 10 số
            "email": "test@example.com",
            "address": "123 Test Street",
            "payment_method": "Tiền mặt khi nhận hàng"
        }
        res = self.client.post("/checkout", data=invalid_data)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Số điện thoại gồm 10 chữ số".encode("utf-8"), res.data)

    def test_10_admin_orders_filter_and_search(self):
        """Màn hình ⑩: Lọc đơn theo tab trạng thái và tìm kiếm theo tên/SĐT"""
        # Lọc tab 'Chờ xác nhận'
        res_tab = self.client.get("/admin/orders?status=Chờ+xác+nhận")
        self.assertEqual(res_tab.status_code, 200)

        # Tìm kiếm theo tên khách hàng 'Nguyễn Văn An'
        res_search = self.client.get("/admin/orders?q=Nguyễn+Văn+An")
        self.assertEqual(res_search.status_code, 200)
        self.assertIn("Nguyễn Văn An".encode("utf-8"), res_search.data)


if __name__ == "__main__":
    unittest.main()
