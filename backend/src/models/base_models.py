from sqlalchemy import Column, String, JSON, DateTime, Boolean, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
import uuid

Base = declarative_base()


# Enums for status fields
class OrderStatus(str, enum.Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"
    RETURNED = "Returned"


class CustomerStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"


class ProductCategory(str, enum.Enum):
    CHAIR = "Chair"
    TABLE = "Table"
    SOFA = "Sofa"
    BED = "Bed"
    CABINET = "Cabinet"
    LAMP = "Lamp"
    DECOR = "Decor"
    OTHER = "Other"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    status = Column(Enum(CustomerStatus), default=CustomerStatus.ACTIVE)
    contact_info = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Customer {self.username} ({self.email})>"


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    description = Column(String)
    category = Column(Enum(ProductCategory))
    price = Column(Float)
    sku = Column(String, unique=True)
    stock_quantity = Column(Integer, default=0)
    dimensions = Column(JSON)  # {width, height, depth, unit}
    weight = Column(Float)
    materials = Column(JSON)  # Array of materials
    images = Column(JSON)  # Array of image URLs
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Product {self.name} ({self.sku})>"


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, index=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    total_amount = Column(Float)
    shipping_address = Column(JSON)
    billing_address = Column(JSON)
    payment_method = Column(String)
    payment_status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)

    # Products in this order with delivery dates
    items = Column(JSON)  # Array of {product_id, quantity, price, delivery_date}

    def __repr__(self):
        return f"<Order {self.id} - {self.status}>"


class SupportAgent(Base):
    __tablename__ = "support_agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    permissions = Column(JSON)  # Array of permission strings
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SupportAgent {self.username} ({self.email})>"


# Initialize database
def init_base_models():
    from backend.src.database import engine

    Base.metadata.create_all(bind=engine)
