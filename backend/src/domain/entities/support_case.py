"""SupportCase entity."""

from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from . import Base


class SupportCase(Base):
    __tablename__ = "support_cases"

    case_id = Column(UUID, primary_key=True)
    customer_id = Column(UUID, nullable=False)  # Removed FK constraint temporarily
    order_id = Column(
        String(255), nullable=False
    )  # Changed from UUID to String for external order IDs
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(
        Enum("open", "in_progress", "resolved", "closed", name="case_status"),
        default="open",
    )
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime)

    # Relationships removed temporarily to fix startup issue
    # customer = relationship("Customer", back_populates="support_cases")
    # refund_cases = relationship("RefundCase", back_populates="support_case")  # Disabled due to FK constraint issues
    # order_reference = relationship("OrderReference", back_populates="support_cases")
