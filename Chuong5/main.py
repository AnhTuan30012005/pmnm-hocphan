from flask import Flask, render_template, request

app = Flask(__name__, template_folder="templates")

def parse_number(val_str):
    """Chuyển chuỗi thành float, chấp nhận cả dấu phẩy (ví dụ: '2,5' -> 2.5)"""
    if not val_str:
        return None
    cleaned = val_str.strip().replace(",", ".")
    return float(cleaned)

def format_number(num):
    """In số nguyên nếu không có phần thập phân (5.0 -> 5), ngược lại in float (3.5 -> 3.5)"""
    if num.is_integer():
        return str(int(num))
    return str(num)

def validate_score(val_str):
    """Hàm kiểm tra điểm dùng chung cho cả 3 ô (CC, GK, CK) theo yêu cầu Bài 2"""
    if not val_str or not val_str.strip():
        return None, "Vui lòng nhập một số."
    
    cleaned = val_str.strip().replace(",", ".")
    try:
        score = float(cleaned)
    except ValueError:
        return None, "Vui lòng nhập một số."
    
    if score < 0 or score > 10:
        return None, "Điểm phải từ 0 đến 10."
    
    return score, None

def calculate_grade(cc, gk, ck):
    """Tính điểm học phần và xếp loại học phần (Bài 2)"""
    score = round(cc * 0.1 + gk * 0.3 + ck * 0.6, 1)
    
    # Điểm cuối kỳ dưới 1: F (điểm liệt)
    if ck < 1.0:
        return f"{score} · F (điểm thi dưới 1)"
    
    if score >= 8.5:
        grade = "A"
    elif score >= 7.0:
        grade = "B"
    elif score >= 5.5:
        grade = "C"
    elif score >= 4.0:
        grade = "D"
    else:
        grade = "F"
        
    return f"{score} · {grade}"


@app.route("/")
def home():
    return render_template("index.html")


# ==================== BÀI 1: MÁY TÍNH CƠ BẢN ====================
@app.route("/bai1", methods=["GET", "POST"])
def bai1():
    a_str = ""
    b_str = ""
    op = "+"
    errors = {}
    result = None

    if request.method == "POST":
        a_str = request.form.get("a", "").strip()
        op = request.form.get("op", "").strip()
        b_str = request.form.get("b", "").strip()

        val_a = None
        val_b = None

        if not a_str:
            errors["a"] = "Vui lòng nhập một số."
        else:
            try:
                val_a = parse_number(a_str)
            except ValueError:
                errors["a"] = "Phải nhập một số."

        valid_ops = ["+", "-", "*", "/"]
        if op not in valid_ops:
            errors["op"] = "Phép toán không hợp lệ."

        if not b_str:
            errors["b"] = "Vui lòng nhập một số."
        else:
            try:
                val_b = parse_number(b_str)
            except ValueError:
                errors["b"] = "Phải nhập một số."

        if "b" not in errors and op == "/" and val_b == 0:
            errors["b"] = "Không thể chia cho 0."

        if not errors:
            if op == "+":
                res = val_a + val_b
            elif op == "-":
                res = val_a - val_b
            elif op == "*":
                res = val_a * val_b
            elif op == "/":
                res = val_a / val_b

            result = f"{format_number(val_a)} {op} {format_number(val_b)} = {format_number(res)}"

    return render_template(
        "bai1.html",
        a=a_str,
        b=b_str,
        op=op,
        errors=errors,
        result=result
    )


# ==================== BÀI 2: TÍNH ĐIỂM HỌC PHẦN ====================
@app.route("/bai2", methods=["GET", "POST"])
def bai2():
    cc_str = ""
    gk_str = ""
    ck_str = ""
    errors = {}
    result = None

    if request.method == "POST":
        cc_str = request.form.get("cc", "").strip()
        gk_str = request.form.get("gk", "").strip()
        ck_str = request.form.get("ck", "").strip()

        val_cc, err_cc = validate_score(cc_str)
        if err_cc:
            errors["cc"] = err_cc

        val_gk, err_gk = validate_score(gk_str)
        if err_gk:
            errors["gk"] = err_gk

        val_ck, err_ck = validate_score(ck_str)
        if err_ck:
            errors["ck"] = err_ck

        if not errors:
            result = calculate_grade(val_cc, val_gk, val_ck)

    return render_template(
        "bai2.html",
        cc=cc_str,
        gk=gk_str,
        ck=ck_str,
        errors=errors,
        result=result
    )


# ==================== BÀI 3: TÍNH CHỈ SỐ BMI ====================
@app.route("/bai3", methods=["GET", "POST"])
def bai3():
    cao_str = ""
    nang_str = ""
    errors = {}
    result = None
    color = "green"

    if request.method == "POST":
        cao_str = request.form.get("cao", "").strip()
        nang_str = request.form.get("nang", "").strip()

        val_cao = None
        val_nang = None

        # 1. Kiểm tra Chiều cao (cm): 50 đến 250
        if not cao_str:
            errors["cao"] = "Vui lòng nhập một số."
        else:
            try:
                val_cao = parse_number(cao_str)
                if val_cao < 50 or val_cao > 250:
                    if val_cao <= 3.0:
                        errors["cao"] = "Giá trị phải từ 50 đến 250. (nhập mét thay vì cm)"
                    else:
                        errors["cao"] = "Giá trị phải từ 50 đến 250."
            except ValueError:
                errors["cao"] = "Vui lòng nhập một số."

        # 2. Kiểm tra Cân nặng (kg): 10 đến 300
        if not nang_str:
            errors["nang"] = "Vui lòng nhập một số."
        else:
            try:
                val_nang = parse_number(nang_str)
                if val_nang < 10 or val_nang > 300:
                    errors["nang"] = "Giá trị phải từ 10 đến 300."
            except ValueError:
                errors["nang"] = "Vui lòng nhập một số."

        # 3. Nếu không có lỗi -> Tính chỉ số BMI
        if not errors:
            h_m = val_cao / 100.0
            bmi = round(val_nang / (h_m ** 2), 1)

            # Cân nặng nên có ứng với BMI 18.5 - 22.9
            w_min = round(18.5 * (h_m ** 2), 1)
            w_max = round(22.9 * (h_m ** 2), 1)

            # Phân loại theo chuẩn người châu Á:
            # < 18.5: thiếu cân (vàng); < 23: bình thường (xanh); < 25: thừa cân (vàng); còn lại: béo phì (đỏ)
            if bmi < 18.5:
                category = "Thiếu cân"
                color = "yellow"
            elif bmi < 23:
                category = "Bình thường"
                color = "green"
            elif bmi < 25:
                category = "Thừa cân"
                color = "yellow"
            else:
                category = "Béo phì"
                color = "red"

            # Kết quả hiển thị đúng theo slide
            if category == "Bình thường":
                result = f"{bmi} · {category}; nên có {w_min} – {w_max} kg"
            else:
                result = f"{bmi} · {category}"

    return render_template(
        "bai3.html",
        cao=cao_str,
        nang=nang_str,
        errors=errors,
        result=result,
        color=color
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
