from sqlalchemy import create_engine, Column, String, Text, DateTime, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./support_refund.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Enums for status fields
class SupportCaseStatus(str, enum.Enum):
    OPEN = "Open"
    CLOSED = "Closed"


class RefundCaseStatus(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    COMPLETED = "Completed"


class EligibilityStatus(str, enum.Enum):
    ELIGIBLE = "Eligible"
    PARTIALLY_ELIGIBLE = "Partially Eligible"
    INELIGIBLE = "Ineligible"


class SupportCase(Base):
    __tablename__ = "support_cases"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    order_id = Column(String, index=True)
    issue_description = Column(Text)
    status = Column(Enum(SupportCaseStatus), default=SupportCaseStatus.OPEN)
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    products = Column(JSON)
    attachments = Column(JSON)


class RefundCase(Base):
    __tablename__ = "refund_cases"

    id = Column(String, primary_key=True, index=True)
    support_case_id = Column(String, index=True)
    customer_id = Column(String, index=True)
    order_id = Column(String, index=True)
    status = Column(Enum(RefundCaseStatus), default=RefundCaseStatus.PENDING)
    eligibility_status = Column(Enum(EligibilityStatus))
    total_refund_amount = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    agent_id = Column(String, nullable=True)
    products = Column(JSON)


# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
