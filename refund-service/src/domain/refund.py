from datetime import datetime
from typing import List, Optional
from enum import Enum
from uuid import uuid4
from .value_objects.money import Money


class RefundStatus(Enum):
    """Represents the status of an actual refund process"""
    PENDING_PROCESSING = "pending_processing"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RefundMethod(Enum):
    """Represents refund delivery methods"""
    MONEY = "money"
    VOUCHER = "voucher"
    REPLACEMENT = "replacement"


class Refund:
    """Aggregate root representing an actual refund transaction"""

    def __init__(
        self,
        refund_id: str,
        refund_request_id: str,
        customer_id: str,
        order_id: str,
        amount: Money,
        method: RefundMethod,
        status: RefundStatus = RefundStatus.PENDING_PROCESSING,
        processed_at: Optional[datetime] = None,
        failed_reason: Optional[str] = None,
        transaction_id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        self.refund_id = refund_id
        self.refund_request_id = refund_request_id
        self.customer_id = customer_id
        self.order_id = order_id
        self.amount = amount
        self.method = method
        self.status = status
        self.processed_at = processed_at
        self.failed_reason = failed_reason
        self.transaction_id = transaction_id
        self.created_at = created_at or datetime.utcnow()

    def process(self) -> None:
        """Mark refund as being processed"""
        self.status = RefundStatus.PROCESSING

    def complete(self, transaction_id: str) -> None:
        """Mark refund as completed successfully"""
        self.status = RefundStatus.COMPLETED
        self.processed_at = datetime.utcnow()
        self.transaction_id = transaction_id

    def fail(self, reason: str) -> None:
        """Mark refund as failed"""
        self.status = RefundStatus.FAILED
        self.processed_at = datetime.utcnow()
        self.failed_reason = reason

    def cancel(self) -> None:
        """Cancel the refund"""
        if self.status == RefundStatus.COMPLETED:
            raise ValueError("Cannot cancel a completed refund")
        self.status = RefundStatus.CANCELLED

    @property
    def is_completed(self) -> bool:
        """Check if refund is completed"""
        return self.status == RefundStatus.COMPLETED

    @property
    def is_pending(self) -> bool:
        """Check if refund is pending processing"""
        return self.status == RefundStatus.PENDING_PROCESSING

    def to_dict(self) -> dict:
        """Convert refund to dictionary for serialization"""
        return {
            "refund_id": self.refund_id,
            "refund_request_id": self.refund_request_id,
            "customer_id": self.customer_id,
            "order_id": self.order_id,
            "amount": self.amount.to_dict(),
            "method": self.method.value,
            "status": self.status.value,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "failed_reason": self.failed_reason,
            "transaction_id": self.transaction_id,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_approved_request(cls, refund_request_id: str, customer_id: str, order_id: str, 
                             amount: Money, method: RefundMethod) -> 'Refund':
        """Create refund from approved refund request"""
        refund_id = f"RF-{uuid4().hex[:8].upper()}"
        return cls(
            refund_id=refund_id,
            refund_request_id=refund_request_id,
            customer_id=customer_id,
            order_id=order_id,
            amount=amount,
            method=method,
            status=RefundStatus.PENDING_PROCESSING
        )

    def __str__(self) -> str:
        return f"Refund {self.refund_id} (Status: {self.status.value})"

    def __repr__(self) -> str:
        return f"<Refund {self.refund_id} amount={self.amount} method={self.method.value}>"