from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 1-N relationship with Book
    books: Mapped[list["Book"]] = relationship(
        "Book", back_populates="category", lazy="selectin"
    )

    def __repr__(self):
        return f"<Category {self.name}>"


class Book(db.Model):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    publisher: Mapped[str | None] = mapped_column(String(100), default="NXB Đại học Huế")
    year: Mapped[int] = mapped_column(Integer, default=2024)
    price: Mapped[int] = mapped_column(Integer, default=0)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(Text, default="")
    image: Mapped[str | None] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Khóa ngoại liên kết tới Category
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category: Mapped["Category"] = relationship("Category", back_populates="books")

    # Quan hệ với OrderItem
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="book")

    def __repr__(self):
        return f"<Book {self.title}>"


class Order(db.Model):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[str | None] = mapped_column(String(120), default="")
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    note: Mapped[str | None] = mapped_column(String(255), default="")
    payment_method: Mapped[str] = mapped_column(String(50), default="Tiền mặt khi nhận hàng")
    shipping_fee: Mapped[int] = mapped_column(Integer, default=20000)
    subtotal: Mapped[int] = mapped_column(Integer, default=0)
    total_amount: Mapped[int] = mapped_column(Integer, default=0)
    # Trạng thái: 'Chờ xác nhận', 'Đang giao', 'Hoàn tất', 'Đã huỷ'
    status: Mapped[str] = mapped_column(String(50), default="Chờ xác nhận")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 1-N relationship with OrderItem
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="selectin"
    )

    # 1-N relationship with OrderStatusHistory
    status_history: Mapped[list["OrderStatusHistory"]] = relationship(
        "OrderStatusHistory", back_populates="order", cascade="all, delete-orphan", lazy="selectin",
        order_by="OrderStatusHistory.created_at.asc()"
    )

    def __repr__(self):
        return f"<Order #{self.id} - {self.customer_name}>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    # Lưu đơn giá tại thời điểm đặt (không đổi khi giá sách thay đổi)
    unit_price: Mapped[int] = mapped_column(Integer, default=0)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    book: Mapped["Book"] = relationship("Book", back_populates="order_items")

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __repr__(self):
        return f"<OrderItem Order#{self.order_id} Book#{self.book_id} x{self.quantity}>"


class OrderStatusHistory(db.Model):
    __tablename__ = "order_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    note: Mapped[str | None] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    order: Mapped["Order"] = relationship("Order", back_populates="status_history")

    def __repr__(self):
        return f"<History Order#{self.order_id} -> {self.status}>"
