"""SupportCase entity."""

from sqlalchemy import UUID, Column, DateTime, Enum, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SupportCase(Base):
    __tablename__ = "support_cases"

    case_id = Column(UUID, primary_key=True)
    customer_id = Column(UUID, nullable=False)
    order_id = Column(UUID, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(
        Enum("open", "in_progress", "resolved", "closed", name="case_status"),
        default="open",
    )
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime)
