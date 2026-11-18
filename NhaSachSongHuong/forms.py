from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, IntegerField, SelectField,
    RadioField, SubmitField
)
from wtforms.validators import DataRequired, Optional, Email, Regexp, NumberRange, Length

current_year = datetime.now().year

class CheckoutForm(FlaskForm):
    customer_name = StringField(
        "Họ tên *",
        validators=[DataRequired(message="Vui lòng nhập họ và tên."), Length(max=100)]
    )
    phone = StringField(
        "Số điện thoại *",
        validators=[
            DataRequired(message="Vui lòng nhập số điện thoại."),
            Regexp(r"^0\d{9}$", message="Số điện thoại gồm 10 chữ số và bắt đầu bằng số 0.")
        ]
    )
    email = StringField(
        "Email",
        validators=[Optional(), Email(message="Email không đúng định dạng.")]
    )
    address = StringField(
        "Địa chỉ giao hàng *",
        validators=[DataRequired(message="Vui lòng nhập địa chỉ giao hàng."), Length(max=255)]
    )
    note = TextAreaField(
        "Ghi chú",
        validators=[Optional(), Length(max=255)]
    )
    payment_method = RadioField(
        "Phương thức thanh toán *",
        choices=[
            ("Tiền mặt khi nhận hàng", "Tiền mặt khi nhận hàng (COD)"),
            ("Chuyển khoản", "Chuyển khoản ngân hàng")
        ],
        default="Tiền mặt khi nhận hàng",
        validators=[DataRequired()]
    )
    submit = SubmitField("Xác nhận đặt hàng")


class BookForm(FlaskForm):
    title = StringField(
        "Tên sách *",
        validators=[DataRequired(message="Vui lòng nhập tên sách."), Length(max=200)]
    )
    author = StringField(
        "Tác giả *",
        validators=[DataRequired(message="Vui lòng nhập tên tác giả."), Length(max=100)]
    )
    category_id = SelectField(
        "Danh mục *",
        coerce=int,
        validators=[DataRequired(message="Vui lòng chọn danh mục.")]
    )
    publisher = StringField(
        "Nhà xuất bản",
        default="NXB Đại học Huế",
        validators=[Optional(), Length(max=100)]
    )
    year = IntegerField(
        "Năm xuất bản",
        default=current_year,
        validators=[
            DataRequired(message="Vui lòng nhập năm xuất bản."),
            NumberRange(min=1900, max=current_year, message=f"Năm từ 1900 đến {current_year}.")
        ]
    )
    price = IntegerField(
        "Giá (đồng) *",
        validators=[
            DataRequired(message="Vui lòng nhập giá sách."),
            NumberRange(min=1000, message="Giá phải lớn hơn hoặc bằng 1.000 đ.")
        ]
    )
    stock = IntegerField(
        "Tồn kho *",
        validators=[
            NumberRange(min=0, message="Tồn kho không âm.")
        ]
    )
    description = TextAreaField("Mô tả", validators=[Optional()])
    image = FileField(
        "Ảnh bìa",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png", "webp"], "Chỉ chấp nhận file ảnh (JPG, PNG, WEBP).")
        ]
    )
    submit = SubmitField("Lưu sách")


class CategoryForm(FlaskForm):
    name = StringField(
        "Tên danh mục *",
        validators=[DataRequired(message="Vui lòng nhập tên danh mục."), Length(max=100)]
    )
    description = TextAreaField("Mô tả", validators=[Optional(), Length(max=255)])
    submit = SubmitField("+ Thêm danh mục")
