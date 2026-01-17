"""RefundCase domain model following DDD principles."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class RefundStatus(Enum):
    """Refund status enum."""

    PENDING = "pending"
    APPROVED = "approved"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RefundItem:
    """Refund item value object."""

    def __init__(
        self,
        product_id: str,
        product_name: str,
        requested_quantity: int,
        original_unit_price: float,
    ):
        if requested_quantity <= 0:
            raise ValueError("Requested quantity must be positive")
        if original_unit_price <= 0:
            raise ValueError("Original unit price must be positive")

        self.product_id = product_id
        self.product_name = product_name
        self.requested_quantity = requested_quantity
        self.original_unit_price = original_unit_price
        self.total_refund_amount = original_unit_price * requested_quantity

    def __eq__(self, other):
        if not isinstance(other, RefundItem):
            return False
        return (
            self.product_id == other.product_id
            and self.product_name == other.product_name
            and self.requested_quantity == other.requested_quantity
            and self.original_unit_price == other.original_unit_price
        )


@dataclass
class RefundCase:
    """RefundCase domain entity."""

    refund_id: str
    support_case_id: str
    items: List[RefundItem]
    status: RefundStatus
    requested_amount: float
    delivery_date: datetime
    refund_requested_at: datetime
    approved_amount: Optional[float] = None
    refund_approved_at: Optional[datetime] = None
    refund_executed_at: Optional[datetime] = None
    settlement_reference: Optional[str] = None
    failure_reason: Optional[str] = None
    approved_by: Optional[str] = None

    def __post_init__(self):
        """Validate entity invariants."""
        if not self.refund_id:
            raise ValueError("Refund ID is required")
        if not self.support_case_id:
            raise ValueError("Support case ID is required")
        if not self.items:
            raise ValueError("At least one refund item is required")
        if self.requested_amount <= 0:
            raise ValueError("Requested amount must be positive")

        # Calculate requested amount from items if not provided
        calculated_amount = sum(item.total_refund_amount for item in self.items)
        if (
            abs(self.requested_amount - calculated_amount) > 0.01
        ):  # Allow small rounding differences
            raise ValueError("Requested amount must match sum of item amounts")

    def approve(self, amount: float, approved_by: str, approval_time: datetime) -> None:
        """Approve the refund case."""
        if self.status != RefundStatus.PENDING:
            raise ValueError("Only pending refunds can be approved")
        if amount <= 0:
            raise ValueError("Approved amount must be positive")
        if amount > self.requested_amount:
            raise ValueError("Approved amount cannot exceed requested amount")

        self.status = RefundStatus.APPROVED
        self.approved_amount = amount
        self.approved_by = approved_by
        self.refund_approved_at = approval_time

    def execute(self, settlement_reference: str, execution_time: datetime) -> None:
        """Mark refund as executed."""
        if self.status != RefundStatus.APPROVED:
            raise ValueError("Only approved refunds can be executed")

        self.status = RefundStatus.EXECUTED
        self.settlement_reference = settlement_reference
        self.refund_executed_at = execution_time

    def fail(self, reason: str) -> None:
        """Mark refund as failed."""
        if self.status not in [RefundStatus.PENDING, RefundStatus.APPROVED]:
            raise ValueError("Only pending or approved refunds can fail")

        self.status = RefundStatus.FAILED
        self.failure_reason = reason

    def cancel(self) -> None:
        """Cancel the refund case."""
        if self.status == RefundStatus.EXECUTED:
            raise ValueError("Executed refunds cannot be cancelled")

        self.status = RefundStatus.CANCELLED

    def is_within_14_day_window(self, current_date: datetime) -> bool:
        """Check if delivery date is within 14-day refund window."""
        time_delta = current_date - self.delivery_date
        return time_delta.days <= 14

    def calculate_total_requested_amount(self) -> float:
        """Calculate total requested amount from items."""
        return sum(item.total_refund_amount for item in self.items)
