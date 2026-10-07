from flask import Flask, request, jsonify, redirect, url_for, abort, make_response
from markupsafe import escape

app = Flask(__name__)
app.json.ensure_ascii = False
app.config["JSON_AS_ASCII"] = False

# Dữ liệu mẫu theo yêu cầu đề bài
STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An",
        "lop": "K47A",
        "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0},
    },
    "23T1020002": {
        "name": "Trần Thị Bình",
        "lop": "K47A",
        "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0},
    },
    "23T1020003": {
        "name": "Lê Hoàng Cường",
        "lop": "K47B",
        "scores": {"PMMNM": 9.5, "CSDL": 9.0},
    },
    "23T1020004": {
        "name": "Phạm Minh Dũng",
        "lop": "K47B",
        "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0},
    },
    "23T1020005": {
        "name": "Hoàng Thu Hà",
        "lop": "K47A",
        "scores": {},
    },
    "23T1020006": {
        "name": "Võ Quốc Khánh",
        "lop": "K47C",
        "scores": {"PMMNM": 7.5, "MMT": 8.0},
    },
}


# ==========================================
# CÁC HÀM PHỤ VÀ KHUNG TRANG (CÂU 0.3 - 0.4)
# ==========================================

def average(scores):
    """Tính trung bình cộng, làm tròn 2 chữ số; dict rỗng -> None."""
    if not scores:
        return None
    return round(sum(scores.values()) / len(scores), 2)


def rank(avg):
    """Xếp loại dựa trên điểm trung bình."""
    if avg is None:
        return "Chưa có điểm"
    if avg >= 8.5:
        return "Giỏi"
    if avg >= 7.0:
        return "Khá"
    if avg >= 5.0:
        return "Trung bình"
    return "Yếu"


def student_summary(mssv):
    """Trả về dict tóm tắt thông tin sinh viên kèm điểm TB và xếp loại."""
    student = STUDENTS.get(mssv)
    if not student:
        return None
    avg = average(student["scores"])
    return {
        "mssv": mssv,
        "name": student["name"],
        "lop": student["lop"],
        "scores": student["scores"],
        "average": avg,
        "rank": rank(avg),
    }


def layout(title, body):
    """Khung trang HTML hoàn chỉnh có menu chuẩn sinh bằng url_for."""
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)} - Sổ điểm</title>
    <style>
        :root {{
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border: #e2e8f0;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            line-height: 1.6;
            padding: 24px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: var(--card-bg);
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            border: 1px solid var(--border);
        }}
        header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 24px 32px;
        }}
        header h1 {{
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        nav {{
            font-size: 1rem;
            font-weight: 500;
        }}
        nav a {{
            color: #dbeafe;
            text-decoration: none;
            transition: color 0.2s;
        }}
        nav a:hover {{
            color: #ffffff;
            text-decoration: underline;
        }}
        .content {{
            padding: 32px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
            margin-bottom: 24px;
        }}
        th, td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background-color: #f1f5f9;
            font-weight: 600;
            color: #334155;
        }}
        tr:hover td {{
            background-color: #f8fafc;
        }}
        .filter-bar {{
            margin-bottom: 20px;
            padding: 12px 16px;
            background: #f8fafc;
            border-radius: 8px;
            border: 1px solid var(--border);
        }}
        .filter-bar a {{
            text-decoration: none;
            color: var(--primary);
            font-weight: 500;
            margin: 0 6px;
        }}
        .btn {{
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            border: none;
            cursor: pointer;
        }}
        .btn:hover {{
            background: var(--primary-hover);
        }}
        input[type="text"] {{
            padding: 8px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 1rem;
            width: 320px;
            max-width: 100%;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Sổ điểm lớp học</h1>
            <nav>
                <a href="{url_for('home')}">Trang chủ</a> · 
                <a href="{url_for('student_list')}">Sinh viên</a> · 
                <a href="{url_for('search')}">Tìm kiếm</a>
            </nav>
        </header>
        <main class="content">
            {body}
        </main>
    </div>
</body>
</html>"""


# ==========================================
# CÁC ROUTE TẠM THỜI CHO PHẦN 0
# ==========================================

@app.route("/")
def home():
    return layout("Trang chủ", "<p>Trang chủ tạm thời</p>")


@app.route("/students")
def student_list():
    return layout("Sinh viên", "<p>Danh sách sinh viên tạm thời</p>")


@app.route("/search")
def search():
    return layout("Tìm kiếm", "<p>Tìm kiếm tạm thời</p>")


if __name__ == "__main__":
    app.run(debug=True, port=8000)
