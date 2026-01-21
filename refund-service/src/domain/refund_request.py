from datetime import datetime
from typing import List, Optional
from enum import Enum
from uuid import uuid4


class RefundRequestStatus(Enum):
    """Represents the status of a refund request"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RefundRequest:
    """Entity representing a single refund request"""

    def __init__(
        self,
        refund_request_id: str,
        product_ids: List[str],
        request_reason: str,
        evidence_photos: Optional[List[str]] = None,
        status: RefundRequestStatus = RefundRequestStatus.PENDING,
        decision_reason: Optional[str] = None,
        decision_date: Optional[datetime] = None,
        decision_agent_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        is_eligible_for_refund: bool = True
    ):
        self.refund_request_id = refund_request_id
        self.product_ids = product_ids
        self.request_reason = request_reason
        self.evidence_photos = evidence_photos or []
        self.status = status
        self.decision_reason = decision_reason
        self.decision_date = decision_date
        self.decision_agent_id = decision_agent_id
        self.created_at = created_at or datetime.utcnow()
        self.is_eligible_for_refund = is_eligible_for_refund

    @property
    def has_required_data(self) -> bool:
        """Check if refund request has minimum required data"""
        return (len(self.product_ids) > 0 and 
                len(self.request_reason) > 0 and 
                len(self.evidence_photos) > 0)

    def approve(
        self,
        agent_id: str,
        decision_reason: str
    ) -> None:
        """Approve the refund request"""
        self.status = RefundRequestStatus.APPROVED
        self.decision_reason = decision_reason
        self.decision_agent_id = agent_id
        self.decision_date = datetime.utcnow()

    def reject(
        self,
        agent_id: str,
        decision_reason: str
    ) -> None:
        """Reject the refund request"""
        self.status = RefundRequestStatus.REJECTED
        self.decision_reason = decision_reason
        self.decision_agent_id = agent_id
        self.decision_date = datetime.utcnow()

    def __str__(self) -> str:
        return f"RefundRequest {self.refund_request_id} ({self.status.value})"

    def __repr__(self) -> str:
        return f"<RefundRequest {self.refund_request_id} products={len(self.product_ids)}>"