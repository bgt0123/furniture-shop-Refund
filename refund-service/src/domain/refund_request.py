from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from .refund_decision import RefundDecision
from .refund_response import RefundResponse
from .value_objects.money import Money


class RefundRequestStatus(Enum):
    """Represents the status of a refund request"""
    SUBMITTED = "pending"  # Initial submission - maps to 'pending' in frontend/database
    UNDER_REVIEW = "pending"  # Under review also shows as pending
    DECISION_MADE = "decision_made"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    APPROVED = "approved"
    REJECTED = "rejected"


class RefundRequest:
    """Aggregate root representing a customer's refund request"""

    def __init__(
        self,
        refund_request_id: str,
        support_case_number: str,
        customer_id: str,
        product_ids: list[str],
        request_reason: str,
        evidence_photos: list[str] | None = None,
        status: RefundRequestStatus = RefundRequestStatus.SUBMITTED,
        order_id: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        responses: list['RefundResponse'] | None = None,
        decisions: list['RefundDecision'] | None = None,
        refund_id: str | None = None  # Link to actual refund entity
    ):
        self.refund_request_id = refund_request_id
        self.support_case_number = support_case_number
        self.customer_id = customer_id
        self.product_ids = product_ids
        self.request_reason = request_reason
        self.evidence_photos = evidence_photos or []
        self.status = status
        self.order_id = order_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or self.created_at  # Default to created_at
        self.responses = responses or []
        self.decisions = decisions or []
        self.refund_id = refund_id

    @property
    def has_minimum_data(self) -> bool:
        """Check if refund request has minimum required data"""
        return (
            bool(self.support_case_number) and
            bool(self.customer_id) and
            len(self.product_ids) > 0 and
            len(self.request_reason) > 0
        )

    def mark_under_review(self) -> None:
        """Mark request as under review"""
        self.status = RefundRequestStatus.UNDER_REVIEW

    def mark_decision_made(self) -> None:
        """Mark that a decision has been made"""
        self.status = RefundRequestStatus.DECISION_MADE

    def mark_completed(self, refund_id: str) -> None:
        """Mark request as completed with refund processed"""
        self.status = RefundRequestStatus.COMPLETED
        self.refund_id = refund_id

    def cancel(self) -> None:
        """Cancel the refund request"""
        self.status = RefundRequestStatus.CANCELLED

    def approve(self, agent_id: str, response_content: str, refund_amount: Optional[Money]) -> None:
        """Approve the refund request"""
        self.status = RefundRequestStatus.APPROVED

    def reject(self, agent_id: str, response_content: str) -> None:
        """Reject the refund request"""
        self.status = RefundRequestStatus.REJECTED

    def request_additional_evidence(self, agent_id: str, response_content: str) -> None:
        """Request additional evidence for the refund request"""
        self.status = RefundRequestStatus.UNDER_REVIEW

    def add_response(
        self,
        response: 'RefundResponse'
    ) -> None:
        """Add a refund response to this request"""
        if response.refund_request_id != self.refund_request_id:
            raise ValueError("Response does not belong to this refund request")
        self.responses.append(response)

    def add_decision(
        self,
        decision: 'RefundDecision'
    ) -> None:
        """Add a refund decision to this request"""
        if decision.refund_request_id != self.refund_request_id:
            raise ValueError("Decision does not belong to this refund request")
        self.decisions.append(decision)

    @property
    def latest_response(self) -> Optional['RefundResponse']:
        """Get the latest response for this refund request"""
        if not self.responses:
            return None
        return sorted(self.responses, key=lambda r: r.timestamp)[-1]

    @property
    def latest_decision(self) -> Optional['RefundDecision']:
        """Get the latest decision for this refund request"""
        if not self.decisions:
            return None
        return sorted(self.decisions, key=lambda d: d.decision_date)[-1]

    @property
    def is_resolved(self) -> bool:
        """Check if refund request has been resolved"""
        return self.status in [RefundRequestStatus.DECISION_MADE, RefundRequestStatus.COMPLETED, RefundRequestStatus.CANCELLED]

    def _map_enum_to_db_status(self, status: RefundRequestStatus) -> str:
        """Map RefundRequestStatus enum values to database/frontend expected values"""
        status_mapping = {
            RefundRequestStatus.SUBMITTED: "pending",
            RefundRequestStatus.UNDER_REVIEW: "pending",
            RefundRequestStatus.APPROVED: "approved",
            RefundRequestStatus.REJECTED: "rejected",
            RefundRequestStatus.DECISION_MADE: "decision_made",
            RefundRequestStatus.COMPLETED: "completed",
            RefundRequestStatus.CANCELLED: "cancelled"
        }
        return status_mapping.get(status, "pending")

    def to_dict(self) -> dict:
        """Convert refund request to dictionary for serialization"""
        latest_decision = self.latest_decision
        return {
            "refund_request_id": self.refund_request_id,
            "support_case_number": self.support_case_number,
            "customer_id": self.customer_id,
            "order_id": self.order_id,
            "product_ids": self.product_ids,
            "request_reason": self.request_reason,
            "evidence_photos": self.evidence_photos,
            "status": self._map_enum_to_db_status(self.status),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "latest_decision": latest_decision.to_dict() if latest_decision else None,
            "responses": [response.to_dict() for response in self.responses],
            "refund_id": self.refund_id
        }

    @classmethod
    def create(
        cls,
        support_case_number: str,
        customer_id: str,
        product_ids: list[str],
        request_reason: str,
        evidence_photos: list[str] | None = None,
        order_id: str | None = None
    ) -> 'RefundRequest':
        """Factory method to create a new refund request"""
        refund_request_id = f"RR-{uuid4().hex[:8].upper()}"
        return cls(
            refund_request_id=refund_request_id,
            support_case_number=support_case_number,
            customer_id=customer_id,
            product_ids=product_ids,
            request_reason=request_reason,
            evidence_photos=evidence_photos,
            order_id=order_id
        )

    def __str__(self) -> str:
        return f"RefundRequest {self.refund_request_id} ({self.status.value})"

    def __repr__(self) -> str:
        return f"<RefundRequest {self.refund_request_id} products={len(self.product_ids)} status={self.status.value}>"
