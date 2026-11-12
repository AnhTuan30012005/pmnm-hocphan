import unittest
from app import app, db, Category, Book

class LibraryMSTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        cls.client = app.test_client()

    # --- 1. TEST DASHBOARD ---
    def test_01_dashboard(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Tổng Quan Thư Viện".encode("utf-8"), response.data)
        self.assertIn("Phân Bố Sách Theo Danh Mục".encode("utf-8"), response.data)

    def test_02_api_stats(self):
        response = self.client.get("/api/dashboard/stats")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("total_categories", data)
        self.assertIn("total_books", data)
        self.assertGreaterEqual(data["total_categories"], 5)
        self.assertGreaterEqual(data["total_books"], 10)

    # --- 2. TEST CRUD CATEGORY ---
    def test_03_list_categories(self):
        response = self.client.get("/categories")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Công nghệ thông tin".encode("utf-8"), response.data)

    def test_04_add_category(self):
        response = self.client.post("/categories/add", data={
            "name": "Tâm lý học",
            "description": "Sách nghiên cứu hành vi và nhận thức"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Tâm lý học".encode("utf-8"), response.data)

    def test_05_add_duplicate_category(self):
        response = self.client.post("/categories/add", data={
            "name": "Công nghệ thông tin",
            "description": "Trùng tên danh mục"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("đã tồn tại".encode("utf-8"), response.data)

    def test_06_edit_category(self):
        with app.app_context():
            cat = Category.query.filter_by(name="Tâm lý học").first()
            cat_id = cat.id

        response = self.client.post(f"/categories/edit/{cat_id}", data={
            "name": "Tâm lý học hành vi",
            "description": "Mô tả mới"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Tâm lý học hành vi".encode("utf-8"), response.data)

    # --- 3. TEST CRUD BOOK THEO DANH MỤC ---
    def test_07_list_books(self):
        response = self.client.get("/books")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Lập trình Python".encode("utf-8"), response.data)

    def test_08_filter_books_by_category(self):
        with app.app_context():
            cat = Category.query.filter_by(name="Công nghệ thông tin").first()
            cat_id = cat.id
        response = self.client.get(f"/books?category_id={cat_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Công nghệ thông tin".encode("utf-8"), response.data)

    def test_09_add_book(self):
        with app.app_context():
            cat = Category.query.first()
            cat_id = cat.id

        response = self.client.post("/books/add", data={
            "title": "Thiết Kế Mẫu (Design Patterns)",
            "author": "Gang of Four",
            "category_id": cat_id,
            "year": 2022,
            "price": 195000,
            "quantity": 6,
            "available": "on"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Thiết Kế Mẫu (Design Patterns)".encode("utf-8"), response.data)

    def test_10_book_detail(self):
        with app.app_context():
            book = Book.query.first()
            book_id = book.id

        response = self.client.get(f"/books/{book_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Chi Tiết Sách".encode("utf-8"), response.data)

    def test_11_edit_book(self):
        with app.app_context():
            book = Book.query.filter_by(title="Thiết Kế Mẫu (Design Patterns)").first()
            book_id = book.id
            cat_id = book.category_id

        response = self.client.post(f"/books/edit/{book_id}", data={
            "title": "Thiết Kế Mẫu (Design Patterns) - Tái Bản",
            "author": "Gang of Four",
            "category_id": cat_id,
            "year": 2024,
            "price": 210000,
            "quantity": 12,
            "available": "on"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Tái Bản".encode("utf-8"), response.data)

    def test_12_delete_book(self):
        with app.app_context():
            book = Book.query.filter_by(title="Thiết Kế Mẫu (Design Patterns) - Tái Bản").first()
            book_id = book.id

        response = self.client.post(f"/books/delete/{book_id}", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Đã xóa cuốn sách".encode("utf-8"), response.data)

    # --- 4. TEST REST APIs ---
    def test_13_api_categories(self):
        response = self.client.get("/api/categories")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 5)

    def test_14_api_books(self):
        response = self.client.get("/api/books")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 10)

if __name__ == "__main__":
    unittest.main()
