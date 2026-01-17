"""Refund case aggregate root domain model."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from src.domain.value_objects.refund_status import RefundStatus
from src.domain.value_objects.delivery_window_validator import DeliveryWindowValidator
from src.domain.entities.refund_item import RefundItem


class RefundCaseAggregate:
    """Aggregate root for refund cases with business logic."""

    def __init__(
        self,
        refund_id: UUID,
        support_case_id: UUID,
        refund_items: list[RefundItem],
        delivery_date: datetime,
        refund_requested_at: Optional[datetime] = None,
        status: RefundStatus = RefundStatus.PENDING,
        requested_amount: Optional[float] = None,
        approved_amount: Optional[float] = None,
        refund_approved_at: Optional[datetime] = None,
        refund_executed_at: Optional[datetime] = None,
        settlement_reference: Optional[str] = None,
        failure_reason: Optional[str] = None,
        approved_by: Optional[UUID] = None,
    ):
        """Initialize refund case aggregate."""
        self.refund_id = refund_id
        self.support_case_id = support_case_id
        self.refund_items = refund_items
        self.delivery_date = delivery_date
        self.refund_requested_at = refund_requested_at or datetime.now()
        self.status = status
        self.requested_amount = requested_amount or self._calculate_requested_amount()
        self.approved_amount = approved_amount
        self.refund_approved_at = refund_approved_at
        self.refund_executed_at = refund_executed_at
        self.settlement_reference = settlement_reference
        self.failure_reason = failure_reason
        self.approved_by = approved_by

    def _calculate_requested_amount(self) -> float:
        """Calculate requested amount from refund items."""
        return sum(item.total_refund_amount for item in self.refund_items)

    def approve_refund(
        self,
        agent_id: UUID,
        current_date: datetime,
        approved_amount: Optional[float] = None,
    ) -> None:
        """Approve refund with delivery window validation.

        Args:
            agent_id: ID of approving support agent
            current_date: Current date for validation
            approved_amount: Approved amount (defaults to requested amount)

        Raises:
            ValueError: If delivery window has expired
            ValueError: If refund case is not in pending status
        """
        # Validate refund case is in pending status
        if self.status != RefundStatus.PENDING:
            raise ValueError(f"Cannot approve refund case in {self.status} status")

        # Validate delivery window
        validator = DeliveryWindowValidator(self.delivery_date)
        if not validator.is_within_14_days(current_date):
            raise ValueError(
                "Refund approval window has expired (14-day delivery window)"
            )

        # Set approved amount if not provided
        if approved_amount is None:
            approved_amount = self.requested_amount

        # Validate approved amount doesn't exceed requested amount
        if approved_amount > self.requested_amount:
            raise ValueError("Approved amount cannot exceed requested amount")

        # Update refund case with approval details
        self.status = RefundStatus.APPROVED
        self.approved_amount = approved_amount
        self.refund_approved_at = current_date
        self.approved_by = agent_id

    def cancel_refund(self, agent_id: UUID, current_date: datetime) -> None:
        """Cancel a pending refund case.

        Args:
            agent_id: ID of cancelling support agent
            current_date: Current date for timestamp

        Raises:
            ValueError: If refund case is already approved or executed
        """
        # Validate refund case can be cancelled
        if self.status not in [RefundStatus.PENDING, RefundStatus.FAILED]:
            raise ValueError(f"Cannot cancel refund case in {self.status} status")

        # Update refund case with cancellation details
        self.status = RefundStatus.CANCELLED
        self.refund_approved_at = current_date
        self.approved_by = agent_id

    def execute_refund(self, settlement_reference: Optional[str] = None) -> None:
        """Mark refund as executed.

        Args:
            settlement_reference: Optional settlement reference

        Raises:
            ValueError: If refund case is not in approved status
        """
        if self.status != RefundStatus.APPROVED:
            raise ValueError(f"Cannot execute refund case in {self.status} status")

        self.status = RefundStatus.EXECUTED
        self.refund_executed_at = datetime.now()
        self.settlement_reference = settlement_reference

    def mark_refund_as_failed(self, failure_reason: str) -> None:
        """Mark refund as failed.

        Args:
            failure_reason: Reason for failure
        """
        self.status = RefundStatus.FAILED
        self.failure_reason = failure_reason
