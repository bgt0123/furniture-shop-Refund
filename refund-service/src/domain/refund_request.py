from datetime import datetime
from typing import List, Optional
from enum import Enum
from uuid import uuid4
from .value_objects.money import Money
from .refund_response import RefundResponse


class RefundRequestStatus(Enum):
    """Represents the status of a refund request"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RefundRequest:
    """Aggregate root representing a single refund request"""

    def __init__(
        self,
        refund_request_id: str,
        support_case_number: str,
        customer_id: str,
        product_ids: List[str],
        request_reason: str,
        evidence_photos: Optional[List[str]] = None,
        status: RefundRequestStatus = RefundRequestStatus.PENDING,
        decision_reason: Optional[str] = None,
        refund_amount: Optional[Money] = None,
        decision_date: Optional[datetime] = None,
        decision_agent_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        responses: Optional[List['RefundResponse']] = None
    ):
        self.refund_request_id = refund_request_id
        self.support_case_number = support_case_number
        self.customer_id = customer_id
        self.product_ids = product_ids
        self.request_reason = request_reason
        self.evidence_photos = evidence_photos or []
        self.status = status
        self.decision_reason = decision_reason
        self.refund_amount = refund_amount
        self.decision_date = decision_date
        self.decision_agent_id = decision_agent_id
        self.created_at = created_at or datetime.utcnow()
        self.responses = responses or []

    @property
    def has_minimum_data(self) -> bool:
        """Check if refund request has minimum required data"""
        return (
            bool(self.support_case_number) and
            bool(self.customer_id) and
            len(self.product_ids) > 0 and 
            len(self.request_reason) > 0
        )

    def add_response(
        self,
        response: 'RefundResponse'
    ) -> None:
        """Add a refund response to this request"""
        if response.refund_request_id != self.refund_request_id:
            raise ValueError("Response does not belong to this refund request")
        self.responses.append(response)

    def approve(
        self,
        agent_id: str,
        decision_reason: str,
        refund_amount: Money
    ) -> None:
        """Approve the refund request with refund amount"""
        if self.status != RefundRequestStatus.PENDING:
            raise ValueError("Cannot approve a non-pending refund request")
        
        self.status = RefundRequestStatus.APPROVED
        self.decision_reason = decision_reason
        self.refund_amount = refund_amount
        self.decision_agent_id = agent_id
        self.decision_date = datetime.utcnow()

    def reject(
        self,
        agent_id: str,
        decision_reason: str
    ) -> None:
        """Reject the refund request"""
        if self.status != RefundRequestStatus.PENDING:
            raise ValueError("Cannot reject a non-pending refund request")
            
        self.status = RefundRequestStatus.REJECTED
        self.decision_reason = decision_reason
        self.decision_agent_id = agent_id
        self.decision_date = datetime.utcnow()

    def request_additional_evidence(
        self,
        agent_id: str,
        request_reason: str
    ) -> None:
        """Request additional evidence for the refund request"""
        if self.status != RefundRequestStatus.PENDING:
            raise ValueError("Cannot request additional evidence for a non-pending refund request")
            
        self.decision_reason = f"Additional evidence requested: {request_reason}"
        self.decision_agent_id = agent_id
        self.decision_date = datetime.utcnow()
        # Status remains PENDING when requesting more evidence

    @property
    def latest_response(self) -> Optional['RefundResponse']:
        """Get the latest response for this refund request"""
        if not self.responses:
            return None
        return sorted(self.responses, key=lambda r: r.timestamp)[-1]

    @property
    def is_resolved(self) -> bool:
        """Check if refund request has been resolved"""
        return self.status != RefundRequestStatus.PENDING

    def to_dict(self) -> dict:
        """Convert refund request to dictionary for serialization"""
        return {
            "refund_request_id": self.refund_request_id,
            "support_case_number": self.support_case_number,
            "customer_id": self.customer_id,
            "product_ids": self.product_ids,
            "request_reason": self.request_reason,
            "evidence_photos": self.evidence_photos,
            "status": self.status.value,
            "decision_reason": self.decision_reason,
            "refund_amount": self.refund_amount.to_dict() if self.refund_amount else None,
            "decision_date": self.decision_date.isoformat() if self.decision_date else None,
            "decision_agent_id": self.decision_agent_id,
            "created_at": self.created_at.isoformat(),
            "responses": [response.to_dict() for response in self.responses]
        }

    def __str__(self) -> str:
        return f"RefundRequest {self.refund_request_id} ({self.status.value})"

    def __repr__(self) -> str:
        return f"<RefundRequest {self.refund_request_id} products={len(self.product_ids)} status={self.status.value}>"