"""RefundCase entity."""

from sqlalchemy import DECIMAL, UUID, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from . import Base


class RefundCase(Base):
    __tablename__ = "refund_cases"

    refund_id = Column(UUID, primary_key=True)
    support_case_id = Column(UUID, ForeignKey("support_cases.case_id"), nullable=False)
    status = Column(
        Enum(
            "pending",
            "approved",
            "executed",
            "failed",
            "cancelled",
            name="refund_status",
        ),
        default="pending",
    )
    requested_amount = Column(DECIMAL(10, 2), nullable=False)
    approved_amount = Column(DECIMAL(10, 2))
    delivery_date = Column(DateTime, nullable=False)
    refund_requested_at = Column(DateTime, nullable=False)
    refund_approved_at = Column(DateTime)
    refund_executed_at = Column(DateTime)
    settlement_reference = Column(String(255))
    failure_reason = Column(String)
    approved_by = Column(UUID, ForeignKey("support_agents.agent_id"))

    # support_case = relationship("SupportCase", back_populates="refund_cases")  # Disabled due to FK constraint issues
    # refund_items = relationship("RefundItem", back_populates="refund_case")  # Disabled due to FK constraint issues
    # approved_by_agent = relationship("SupportAgent", back_populates="approved_refunds")  # Disabled due to FK constraint issues
