import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    JSON,
    Enum as SQLAlchemyEnum,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID
from database.session import Base


class RefundCaseStatus(str, Enum):
    """Refund case status enum."""

    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    COMPLETED = "Completed"


class EligibilityStatus(str, Enum):
    """Refund eligibility status enum."""

    ELIGIBLE = "Eligible"
    PARTIALLY_ELIGIBLE = "Partially Eligible"
    INELIGIBLE = "Ineligible"


class RefundCase(Base):
    """Refund case domain model."""

    __tablename__ = "refund_cases"

    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    support_case_id = Column(String(36), nullable=False, index=True)
    customer_id = Column(String(36), nullable=False, index=True)
    order_id = Column(String(20), nullable=False, index=True)
    products = Column(JSON, nullable=False)
    total_refund_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(
        SQLAlchemyEnum(RefundCaseStatus),
        default=RefundCaseStatus.PENDING,
        nullable=False,
        server_default=RefundCaseStatus.PENDING.name,
    )
    eligibility_status = Column(SQLAlchemyEnum(EligibilityStatus), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    agent_id = Column(String(36), nullable=True, index=True)

    def __repr__(self):
        return (
            f"<RefundCase {self.id} - {self.status.value} - {self.total_refund_amount}>"
        )

    def approve(self, agent_id: uuid.UUID, processed_at: Optional[datetime] = None):
        """Approve refund case."""
        if self.status == RefundCaseStatus.PENDING:
            self.status = RefundCaseStatus.APPROVED
            self.agent_id = agent_id
            self.processed_at = processed_at or datetime.utcnow()

    def reject(
        self, agent_id: uuid.UUID, reason: str, processed_at: Optional[datetime] = None
    ):
        """Reject refund case."""
        if self.status == RefundCaseStatus.PENDING:
            self.status = RefundCaseStatus.REJECTED
            self.agent_id = agent_id
            self.rejection_reason = reason
            self.processed_at = processed_at or datetime.utcnow()

    def complete(self):
        """Mark refund case as completed."""
        if self.status in [RefundCaseStatus.APPROVED, RefundCaseStatus.REJECTED]:
            self.status = RefundCaseStatus.COMPLETED
