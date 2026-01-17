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
from .refund_eligibility import EligibilityStatus


class RefundCaseStatus(str, Enum):
    """Refund case status enum."""

    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    COMPLETED = "Completed"


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
    reason = Column(Text, nullable=False)

    def __repr__(self):
        return (
            f"<RefundCase {self.id} - {self.status.value} - {self.total_refund_amount}>"
        )

    def approve(self, agent_id: uuid.UUID, processed_at: Optional[datetime] = None):
        """Approve refund case."""
        if self.status == RefundCaseStatus.PENDING:
            self.status = RefundCaseStatus.APPROVED
            self.agent_id = str(agent_id)
            self.processed_at = processed_at or datetime.utcnow()

    def reject(
        self, agent_id: uuid.UUID, reason: str, processed_at: Optional[datetime] = None
    ):
        """Reject refund case."""
        if self.status == RefundCaseStatus.PENDING:
            self.status = RefundCaseStatus.REJECTED
            self.agent_id = str(agent_id)
            self.rejection_reason = reason
            self.processed_at = processed_at or datetime.utcnow()

    def complete(self):
        """Mark refund case as completed."""
        if self.status in [RefundCaseStatus.APPROVED, RefundCaseStatus.REJECTED]:
            self.status = RefundCaseStatus.COMPLETED

    def calculate_total_refund_amount(self, products: List[Dict[str, Any]]) -> float:
        """Calculate total refund amount based on eligible products."""
        total_amount = 0.0
        for product in products:
            price = float(product.get("price", 0))
            quantity = product.get("quantity", 1)
            total_amount += price * quantity
        return total_amount

    def determine_eligibility(self, products: List[Dict[str, Any]]) -> str:
        """Determine eligibility status based on delivery dates."""
        # Basic implementation - can be enhanced with RefundEligibility class
        from datetime import datetime, date

        eligible_count = 0
        total_count = len(products)

        for product in products:
            delivery_date_str = product.get("delivery_date")
            if delivery_date_str:
                try:
                    delivery_date = datetime.strptime(
                        delivery_date_str, "%Y-%m-%d"
                    ).date()
                    days_diff = (datetime.utcnow().date() - delivery_date).days
                    if days_diff <= 14:  # 14-day refund window
                        eligible_count += 1
                except ValueError:
                    # If date parsing fails, treat as ineligible
                    pass

        if eligible_count == total_count:
            return EligibilityStatus.ELIGIBLE
        elif eligible_count == 0:
            return EligibilityStatus.INELIGIBLE
        else:
            return EligibilityStatus.PARTIALLY_ELIGIBLE
