import unittest
from app import app, BOOKS


class LibraryMSTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_books_data(self):
        """1. Kiểm tra list BOOKS >= 4 cuốn và đủ các trường bắt buộc."""
        self.assertGreaterEqual(len(BOOKS), 4)
        for b in BOOKS:
            self.assertIn("id", b)
            self.assertIn("title", b)
            self.assertIn("author", b)
            self.assertIn("year", b)
            self.assertIn("category", b)
            self.assertIn("available", b)

    def test_index_route(self):
        """2. Kiểm tra route /: tổng số đầu sách, số sách sẵn sàng."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        total = str(len(BOOKS))
        available = str(sum(1 for b in BOOKS if b["available"]))
        html = res.data.decode("utf-8")
        self.assertIn("Tổng số đầu sách", html)
        self.assertIn(total, html)
        self.assertIn("Số sách sẵn sàng cho mượn", html)
        self.assertIn(available, html)
        self.assertIn('href="/books"', html)

    def test_books_route(self):
        """3. Kiểm tra route /books: bảng sách, tên sách liên kết, thanh lọc."""
        res = self.client.get("/books")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("<table", html)
        self.assertIn("Lọc theo thể loại:", html)
        for b in BOOKS:
            self.assertIn(f'/books/{b["id"]}', html)
            self.assertIn(b["title"], html)

    def test_books_filter_category(self):
        """3. Kiểm tra lọc ?category=Lập trình."""
        res = self.client.get("/books?category=Lập trình")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Lập trình Python căn bản", html)
        self.assertIn("Lập trình Web với Flask", html)
        self.assertNotIn("Cơ sở dữ liệu nâng cao", html)

    def test_book_detail_success(self):
        """4. Kiểm tra chi tiết /books/<int:book_id> khi tồn tại."""
        res = self.client.get("/books/1")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Lập trình Python căn bản", html)
        self.assertIn("Nguyễn Văn A", html)
        self.assertIn("2021", html)
        self.assertIn("Sẵn sàng cho mượn", html)

    def test_book_detail_not_found(self):
        """4. Kiểm tra /books/<int:book_id> khi không tồn tại -> 404 Không có sách với ID = ..."""
        res = self.client.get("/books/999")
        self.assertEqual(res.status_code, 404)
        html = res.data.decode("utf-8")
        self.assertIn("Không có sách với ID = 999", html)
        self.assertIn('href="/"', html)
        self.assertIn('href="/books"', html)

    def test_api_books(self):
        """5. Kiểm tra /api/books: JSON."""
        res = self.client.get("/api/books")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.is_json)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), len(BOOKS))

    def test_api_books_filter(self):
        """5. Kiểm tra /api/books?category=Lập trình."""
        res = self.client.get("/api/books?category=Lập trình")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data), 2)
        for b in data:
            self.assertEqual(b["category"], "Lập trình")

    def test_api_book_detail_success(self):
        """5. Kiểm tra /api/books/<int:book_id>: JSON chi tiết."""
        res = self.client.get("/api/books/1")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.is_json)
        data = res.get_json()
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["title"], "Lập trình Python căn bản")

    def test_api_book_detail_not_found(self):
        """5. Kiểm tra /api/books/<int:book_id> khi không tồn tại -> 404 JSON {"error": "..."}."""
        res = self.client.get("/api/books/999")
        self.assertEqual(res.status_code, 404)
        self.assertTrue(res.is_json)
        data = res.get_json()
        self.assertIn("error", data)
        self.assertIn("999", data["error"])

    def test_general_404_html(self):
        """6. Kiểm tra URL không tồn tại dạng HTML trả về 404 tùy biến có menu chung."""
        res = self.client.get("/duong-dan-khong-ton-tai")
        self.assertEqual(res.status_code, 404)
        html = res.data.decode("utf-8")
        self.assertIn("404", html)
        self.assertIn('href="/books"', html)

    def test_general_404_api(self):
        """6. Kiểm tra URL API không tồn tại trả về JSON lỗi 404."""
        res = self.client.get("/api/khong-ton-tai")
        self.assertEqual(res.status_code, 404)
        self.assertTrue(res.is_json)
        data = res.get_json()
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
