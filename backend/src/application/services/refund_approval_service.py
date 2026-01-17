"""Refund approval service for handling refund approval workflow."""

from datetime import datetime
from typing import Optional

from src.domain.entities.refund_case import RefundCase
from src.domain.entities.support_agent import SupportAgent
from src.domain.value_objects.delivery_window_validator import DeliveryWindowValidator
from src.domain.value_objects.refund_status import RefundStatus


class RefundApprovalService:
    """Service for handling refund approval business logic."""

    def approve_refund(
        self,
        refund_case: RefundCase,
        agent: SupportAgent,
        current_date: datetime,
        approved_amount: Optional[float] = None,
    ) -> RefundCase:
        """Approve a refund case with delivery window validation.

        Args:
            refund_case: The refund case to approve
            agent: The support agent approving the refund
            current_date: Current date for validation
            approved_amount: Approved amount (defaults to requested amount)

        Returns:
            Updated refund case with approval details

        Raises:
            ValueError: If delivery window has expired
            ValueError: If refund case is not in pending status
        """
        # Convert status string to RefundStatus enum
        current_status = RefundStatus(refund_case.status)

        # Validate refund case is in pending status
        if current_status != RefundStatus.PENDING:
            raise ValueError(
                f"Cannot approve refund case in {refund_case.status} status"
            )

        # Validate delivery window
        validator = DeliveryWindowValidator(refund_case.delivery_date)
        if not validator.is_within_14_days(current_date):
            raise ValueError(
                "Refund approval window has expired (14-day delivery window)"
            )

        # Set approved amount if not provided
        if approved_amount is None:
            approved_amount = (
                float(refund_case.requested_amount)
                if refund_case.requested_amount
                else None
            )

        # Validate approved amount
        if approved_amount and refund_case.requested_amount:
            if approved_amount > float(refund_case.requested_amount):
                raise ValueError("Approved amount cannot exceed requested amount")

        # Update refund case with approval details
        refund_case.status = RefundStatus.APPROVED.value
        refund_case.approved_amount = approved_amount
        refund_case.refund_approved_at = current_date
        refund_case.approved_by = agent.agent_id

        return refund_case

    def cancel_refund(
        self, refund_case: RefundCase, agent: SupportAgent, current_date: datetime
    ) -> RefundCase:
        """Cancel a pending refund case.

        Args:
            refund_case: The refund case to cancel
            agent: The support agent cancelling the refund
            current_date: Current date for timestamp

        Returns:
            Updated refund case with cancellation details

        Raises:
            ValueError: If refund case is already approved or executed
        """
        # Convert status string to RefundStatus enum
        current_status = RefundStatus(refund_case.status)

        # Validate refund case can be cancelled
        if current_status not in [RefundStatus.PENDING, RefundStatus.FAILED]:
            raise ValueError(
                f"Cannot cancel refund case in {refund_case.status} status"
            )

        # Update refund case with cancellation details
        refund_case.status = RefundStatus.CANCELLED.value
        refund_case.refund_approved_at = current_date
        refund_case.approved_by = agent.agent_id

        return refund_case
