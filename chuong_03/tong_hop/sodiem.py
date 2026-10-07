from flask import Flask, request, jsonify, redirect, url_for, abort, make_response
from markupsafe import escape

app = Flask(__name__)
app.json.ensure_ascii = False
app.config["JSON_AS_ASCII"] = False

# Dữ liệu mẫu theo yêu cầu đề bài (chỉ phần này được sao chép từ đề)
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
        .filter-bar a.active {{
            background: var(--primary);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
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
        .info-card {{
            background: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 18px 24px;
            margin-bottom: 24px;
        }}
        .info-card p {{
            margin: 6px 0;
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
# PHẦN 1: GIAO DIỆN WEB (CÂU 1 – 6)
# ==========================================

@app.route("/")
def home():
    """Câu 1. / : tổng số sinh viên, số lớp (không trùng), liên kết đến /students và /api/students."""
    total_students = len(STUDENTS)
    classes = set(sv["lop"] for sv in STUDENTS.values())
    total_classes = len(classes)

    body = f"""
    <h2>Tổng quan hệ thống</h2>
    <div class="info-card">
        <p><strong>Tổng số sinh viên:</strong> {total_students}</p>
        <p><strong>Số lớp học:</strong> {total_classes}</p>
    </div>
    <div style="margin-top: 20px;">
        <p style="margin-bottom: 12px;">
            👉 <a href="{url_for('student_list')}" class="btn">Xem danh sách sinh viên (/students)</a>
        </p>
        <p>
            👉 <a href="{url_for('api_students')}">Truy cập API danh sách sinh viên (/api/students)</a>
        </p>
    </div>
    """
    return layout("Trang chủ", body)


@app.route("/students")
def student_list():
    """Câu 2. /students : danh sách sinh viên, lọc theo lớp ?lop=..."""
    lop_filter = request.args.get("lop", "").strip()

    # Lấy danh sách các lớp duy nhất từ dữ liệu, sắp xếp
    all_classes = sorted(list(set(sv["lop"] for sv in STUDENTS.values())))

    # Tạo thanh lọc: Tất cả | K47A | K47B | K47C
    filter_links = []
    active_all = ' class="active"' if not lop_filter else ''
    filter_links.append(f'<a href="{url_for("student_list")}"{active_all}>Tất cả</a>')

    for c in all_classes:
        active_class = ' class="active"' if lop_filter.upper() == c.upper() else ''
        filter_links.append(f'<a href="{url_for("student_list", lop=c)}"{active_class}>{escape(c)}</a>')

    filter_bar_html = f"""
    <div class="filter-bar">
        <strong>Lọc theo lớp:</strong> {" | ".join(filter_links)}
    </div>
    """

    # Lọc danh sách sinh viên
    filtered_summaries = []
    for mssv in sorted(STUDENTS.keys()):
        summary = student_summary(mssv)
        if lop_filter:
            if summary["lop"].upper() == lop_filter.upper():
                filtered_summaries.append(summary)
        else:
            filtered_summaries.append(summary)

    if not filtered_summaries:
        body = f"""
        <h2>Danh sách sinh viên</h2>
        {filter_bar_html}
        <p style="margin-top: 16px; color: #dc2626; font-style: italic;">Không có sinh viên phù hợp.</p>
        """
        return layout("Danh sách sinh viên", body)

    # Tạo bảng sinh viên
    rows = []
    for s in filtered_summaries:
        avg_display = f"{s['average']}" if s["average"] is not None else "—"
        rows.append(f"""
        <tr>
            <td><a href="{url_for('student_detail', mssv=s['mssv'])}">{escape(s['mssv'])}</a></td>
            <td>{escape(s['name'])}</td>
            <td>{escape(s['lop'])}</td>
            <td>{avg_display}</td>
            <td>{escape(s['rank'])}</td>
        </tr>
        """)

    table_html = f"""
    <table>
        <thead>
            <tr>
                <th>MSSV</th>
                <th>Họ tên</th>
                <th>Lớp</th>
                <th>Điểm TB</th>
                <th>Xếp loại</th>
            </tr>
        </thead>
        <tbody>
            {"".join(rows)}
        </tbody>
    </table>
    """

    body = f"""
    <h2>Danh sách sinh viên</h2>
    {filter_bar_html}
    {table_html}
    """
    return layout("Danh sách sinh viên", body)


@app.route("/students/<mssv>")
def student_detail(mssv):
    """Câu 3. /students/<mssv> : chi tiết sinh viên và bảng điểm từng học phần."""
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")

    summary = student_summary(mssv)
    avg_display = f"{summary['average']}" if summary["average"] is not None else "—"

    # Bảng điểm từng học phần
    score_rows = []
    if summary["scores"]:
        for course, score in summary["scores"].items():
            score_rows.append(f"""
            <tr>
                <td>{escape(course)}</td>
                <td>{score}</td>
            </tr>
            """)
        scores_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Học phần</th>
                    <th>Điểm</th>
                </tr>
            </thead>
            <tbody>
                {"".join(score_rows)}
            </tbody>
        </table>
        """
    else:
        scores_table = "<p><em>Chưa có điểm học phần nào.</em></p>"

    # Liên kết tải CSV (Câu 5) và Link rút gọn (Câu 4)
    csv_url = url_for("export_student_csv", mssv=mssv)
    short_url = url_for("short_student_detail", mssv=mssv)

    body = f"""
    <h2>Chi tiết sinh viên</h2>
    <div class="info-card">
        <p><strong>MSSV:</strong> {escape(summary['mssv'])}</p>
        <p><strong>Họ tên:</strong> {escape(summary['name'])}</p>
        <p><strong>Lớp:</strong> <a href="{url_for('student_list', lop=summary['lop'])}">{escape(summary['lop'])}</a></p>
        <p><strong>Điểm trung bình:</strong> {avg_display}</p>
        <p><strong>Xếp loại:</strong> {escape(summary['rank'])}</p>
        <p><strong>Link rút gọn:</strong> <a href="{short_url}">{short_url}</a></p>
    </div>

    <h3>Bảng điểm học phần</h3>
    {scores_table}

    <div style="margin-top: 20px;">
        <a href="{csv_url}" class="btn">Tải bảng điểm (CSV)</a>
    </div>
    """
    return layout(f"Sinh viên {summary['name']}", body)


@app.route("/sv/<mssv>")
def short_student_detail(mssv):
    """Câu 4. /sv/<mssv> : chuyển hướng tới /students/<mssv> với mã 301."""
    return redirect(url_for("student_detail", mssv=mssv), code=301)


@app.route("/students/<mssv>/export")
def export_student_csv(mssv):
    """Câu 5. /students/<mssv>/export : xuất bảng điểm CSV tải file xuống."""
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")

    student = STUDENTS[mssv]
    lines = ["hoc_phan,diem"]
    for course, score in student["scores"].items():
        lines.append(f"{course},{score}")
    csv_data = "\n".join(lines) + "\n"

    response = make_response(csv_data)
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    return response


@app.route("/search")
def search():
    """Câu 6. /search?q=... : tìm kiếm an toàn, chống XSS."""
    q = request.args.get("q", "")
    escaped_q = escape(q)

    search_result_html = ""
    if "q" in request.args:
        trimmed_q = q.strip().lower()
        matched_students = []
        if trimmed_q:
            for mssv, sv in STUDENTS.items():
                if trimmed_q in sv["name"].lower() or trimmed_q in mssv.lower():
                    matched_students.append(student_summary(mssv))

        result_count = len(matched_students)
        search_result_html = f"<p style='margin-top: 16px;'>Tìm thấy {result_count} kết quả cho “{escaped_q}”</p>"

        if matched_students:
            result_items = []
            for s in matched_students:
                result_items.append(
                    f'<li><a href="{url_for("student_detail", mssv=s["mssv"])}">{escape(s["name"])} ({escape(s["mssv"])} - {escape(s["lop"])})</a></li>'
                )
            search_result_html += f"<ul style='margin: 12px 24px;'>{''.join(result_items)}</ul>"

    body = f"""
    <h2>Tìm kiếm sinh viên</h2>
    <form method="GET" action="{url_for('search')}" style="margin-top: 16px;">
        <input type="text" name="q" value="{escaped_q}" placeholder="Nhập tên hoặc MSSV...">
        <button type="submit" class="btn">Tìm kiếm</button>
    </form>
    {search_result_html}
    """
    return layout("Tìm kiếm", body)


# ==========================================
# PHẦN 2: API JSON (CÂU 7 – 8)
# ==========================================

@app.route("/api/students")
def api_students():
    """Câu 7. GET /api/students : danh sách sinh viên JSON có lọc lop và min_avg."""
    lop_filter = request.args.get("lop", "").strip()

    # Phân biệt trường hợp thiếu tham số và tham số sai kiểu min_avg
    min_avg = None
    if "min_avg" in request.args:
        try:
            min_avg = float(request.args["min_avg"])
        except ValueError:
            abort(400, description="min_avg phải là một số thực.")

    result = []
    for mssv in sorted(STUDENTS.keys()):
        summary = student_summary(mssv)
        # Lọc theo lop (không phân biệt hoa thường)
        if lop_filter and summary["lop"].upper() != lop_filter.upper():
            continue
        # Lọc theo min_avg: chỉ sinh viên có điểm TB >= min_avg, bỏ qua sinh viên chưa có điểm
        if min_avg is not None:
            if summary["average"] is None or summary["average"] < min_avg:
                continue
        result.append(summary)

    return jsonify(result)


@app.route("/api/students/<mssv>")
def api_student_detail(mssv):
    """Câu 7. GET /api/students/<mssv> : thông tin chi tiết một sinh viên dạng JSON."""
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    return jsonify(student_summary(mssv))


@app.route("/api/students/<mssv>/scores/<course>", methods=["GET", "PUT", "DELETE"])
def student_course_score(mssv, course):
    """Câu 8. Quản lý điểm một học phần (GET, PUT, DELETE). Mã học phần lưu hoa."""
    # Mọi method: MSSV không tồn tại -> 404
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")

    student = STUDENTS[mssv]
    course_key = course.upper()

    # 1. GET: Xem điểm
    if request.method == "GET":
        if course_key not in student["scores"]:
            abort(404, description=f"Học phần {course_key} chưa có điểm.")
        return jsonify({
            "mssv": mssv,
            "course": course_key,
            "score": student["scores"][course_key],
        })

    # 2. PUT: Thêm hoặc sửa điểm
    elif request.method == "PUT":
        if "score" not in request.args:
            abort(400, description="Thiếu tham số score.")

        raw_score = request.args["score"]
        try:
            score_val = float(raw_score)
        except ValueError:
            abort(400, description="score phải là một số thực.")

        if score_val < 0 or score_val > 10:
            abort(400, description="score phải nằm trong đoạn [0, 10].")

        # Chuẩn hóa số nguyên nếu không có phần thập phân
        if score_val.is_integer() and "." not in raw_score:
            score_saved = int(score_val)
        else:
            score_saved = score_val

        is_new = course_key not in student["scores"]
        student["scores"][course_key] = score_saved
        new_avg = average(student["scores"])

        response_data = {
            "mssv": mssv,
            "course": course_key,
            "score": score_saved,
            "average": new_avg,
        }

        if is_new:
            # 201 + header Location trỏ về chính URL này
            location_url = url_for("student_course_score", mssv=mssv, course=course_key)
            resp = make_response(jsonify(response_data), 201)
            resp.headers["Location"] = location_url
            return resp
        else:
            # 200
            return jsonify(response_data), 200

    # 3. DELETE: Xoá điểm
    elif request.method == "DELETE":
        if course_key not in student["scores"]:
            abort(404, description=f"Học phần {course_key} chưa có điểm.")
        del student["scores"][course_key]
        return make_response("", 204)


# ==========================================
# PHẦN 3: XỬ LÝ LỖI THỐNG NHẤT (CÂU 9)
# ==========================================

@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_error(error):
    """Xử lý lỗi thống nhất cho 400, 404, 405 phân biệt /api/ (JSON) và HTML."""
    code = getattr(error, "code", 500)
    titles = {
        400: "Dữ liệu không hợp lệ",
        404: "Không tìm thấy",
        405: "Phương thức không được hỗ trợ",
    }
    title = titles.get(code, "Lỗi")
    description = getattr(error, "description", "")

    if request.path.startswith("/api/"):
        return jsonify({
            "error": title,
            "detail": description,
        }), code
    else:
        body = f"""
        <div style="text-align: center; padding: 32px 16px;">
            <h2 style="color: #dc2626; font-size: 1.6rem; margin-bottom: 12px;">Lỗi {code}: {escape(title)}</h2>
            <p style="color: #475569; font-size: 1.05rem; margin-bottom: 24px;">{escape(description)}</p>
            <p><a href="{url_for('home')}" class="btn">← Quay lại Trang chủ</a></p>
        </div>
        """
        return layout(f"Lỗi {code}", body), code


if __name__ == "__main__":
    app.run(debug=True, port=8000)

