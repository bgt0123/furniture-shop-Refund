"""SupportCase entity."""

from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from . import Base


class SupportCase(Base):
    __tablename__ = "support_cases"

    case_id = Column(UUID, primary_key=True)
    customer_id = Column(UUID, ForeignKey("customers.customer_id"), nullable=False)
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

    customer = relationship("Customer", back_populates="support_cases")
    refund_cases = relationship("RefundCase", back_populates="support_case")
