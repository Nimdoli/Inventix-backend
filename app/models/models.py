import uuid
from datetime import datetime, date

from sqlalchemy import Column, String, Integer, Numeric, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True)  # matches auth.users.id from Supabase Auth
    full_name = Column(String)
    role = Column(String)  # "customer" | "supplier"
    store_name = Column(String)
    contact_number = Column(String)

    products = relationship("Product", back_populates="owner")


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)
    stock = Column(Integer, nullable=False)
    status = Column(String, nullable=False)  # "in_stock" | "low_stock" | "out_of_stock"
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("Profile", back_populates="products")


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True)  # "#ORD-0001"
    customer_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    store = Column(String, nullable=False)
    amount = Column(Numeric, nullable=False)
    location = Column(String)
    item_count = Column(Integer)
    status = Column(String, nullable=False)  # "pending" | "delivered"
    order_date = Column(Date, default=date.today)


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(String, primary_key=True)  # "#DEL-0002"
    order_id = Column(String, ForeignKey("orders.id"))
    company = Column(String, nullable=False)
    shipped_date = Column(Date)
    eta_date = Column(Date)
    status = Column(String, nullable=False)  # "pending" | "in_transit" | "delivered"


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    address = Column(String)
    phone = Column(String)
    email = Column(String)
    is_active = Column(Boolean, default=True)


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String)  # "sales" | "inventory"
    file_name = Column(String, nullable=False)
    file_url = Column(String)
    generated_at = Column(DateTime, default=datetime.utcnow)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"))
    status = Column(String, default="draft")  # "draft" | "sent" | "approved"
    quantity = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
