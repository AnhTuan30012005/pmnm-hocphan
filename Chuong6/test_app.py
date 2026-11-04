import unittest
from app import app, db, Student

class StudentTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_1_them_mau(self):
        # Lần gọi đầu hoặc sau khi đã có dữ liệu
        response = self.client.get("/them-mau")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "Đã thêm 5 sinh viên" in response.text or "không thêm nữa" in response.text
        )

    def test_2_thu_truy_van(self):
        response = self.client.get("/thu-truy-van")
        self.assertEqual(response.status_code, 200)
        self.assertIn("1. get(3): <Student 23T1020003 Lê Hoàng Cường>", response.text)
        self.assertIn("2. get(99): None", response.text)
        self.assertIn("6. Số SV: 5, điểm TB: 7.26", response.text)
        self.assertEqual(response.headers.get("Content-Type"), "text/plain; charset=utf-8")

    def test_2_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("23T1020001".encode("utf-8"), response.data)
        self.assertIn("Nguyễn Văn An".encode("utf-8"), response.data)

    def test_3_add_duplicate_mssv(self):
        response = self.client.post("/add", data={
            "mssv": "23T1020001",
            "name": "Trùng MSSV",
            "gpa": "8.0"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("đã tồn tại".encode("utf-8"), response.data)

    def test_4_api_students(self):
        response = self.client.get("/api/students")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIsInstance(json_data, list)
        self.assertGreaterEqual(len(json_data), 5)

if __name__ == "__main__":
    unittest.main()
