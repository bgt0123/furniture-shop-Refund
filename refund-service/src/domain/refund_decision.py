from datetime import datetime
from typing import Optional
from enum import Enum
from uuid import uuid4
from .value_objects.money import Money
from .refund_response import RefundMethod


class DecisionStatus(Enum):
    """Represents the stage of a refund decision"""
    PENDING_REVIEW = "pending_review"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_MORE_EVIDENCE = "needs_more_evidence"


class DecisionType(Enum):
    """Type of decision made"""
    APPROVAL = "approval"
    REJECTION = "rejection"
    REQUEST_ADDITIONAL_EVIDENCE = "request_additional_evidence"


class RefundDecision:
    """Aggregate representing a business decision on a refund request"""

    def __init__(
        self,
        decision_id: str,
        refund_request_id: str,
        agent_id: str,
        decision_type: DecisionType,
        decision_reason: str,
        status: DecisionStatus = DecisionStatus.PENDING_REVIEW,
        refund_amount: Optional[Money] = None,
        refund_method: Optional[RefundMethod] = None,
        requires_additional_review: bool = False,
        reviewer_agent_id: Optional[str] = None,
        decision_date: Optional[datetime] = None,
        created_at: Optional[datetime] = None
    ):
        # Validation
        if decision_type == DecisionType.APPROVAL and refund_amount is None:
            raise ValueError("Approval decisions must include refund amount")
        if decision_type == DecisionType.APPROVAL and refund_method is None:
            raise ValueError("Approval decisions must include refund method")
            
        self.decision_id = decision_id
        self.refund_request_id = refund_request_id
        self.agent_id = agent_id
        self.decision_type = decision_type
        self.decision_reason = decision_reason
        self.status = status
        self.refund_amount = refund_amount
        self.refund_method = refund_method
        self.requires_additional_review = requires_additional_review
        self.reviewer_agent_id = reviewer_agent_id
        self.decision_date = decision_date or datetime.utcnow()
        self.created_at = created_at or datetime.utcnow()

    def approve(self, reviewer_agent_id: Optional[str] = None) -> None:
        """Final approval of the decision"""
        self.status = DecisionStatus.APPROVED
        if reviewer_agent_id:
            self.reviewer_agent_id = reviewer_agent_id
        self.decision_date = datetime.utcnow()

    def reject(self, reviewer_agent_id: Optional[str] = None) -> None:
        """Final rejection of the decision"""
        self.status = DecisionStatus.REJECTED
        if reviewer_agent_id:
            self.reviewer_agent_id = reviewer_agent_id
        self.decision_date = datetime.utcnow()

    def request_more_evidence(self) -> None:
        """Mark as needing more evidence"""
        self.status = DecisionStatus.NEEDS_MORE_EVIDENCE

    def mark_under_review(self, reviewer_agent_id: str) -> None:
        """Mark decision as under active review"""
        self.status = DecisionStatus.UNDER_REVIEW
        self.reviewer_agent_id = reviewer_agent_id

    def escalate_for_review(self) -> None:
        """Escalate for additional review"""
        self.requires_additional_review = True

    @property
    def is_final_decision(self) -> bool:
        """Check if this is a final decision (approved/rejected)"""
        return self.status in [DecisionStatus.APPROVED, DecisionStatus.REJECTED]

    @property
    def is_approval(self) -> bool:
        """Check if this decision is an approval"""
        return self.decision_type == DecisionType.APPROVAL

    def to_dict(self) -> dict:
        """Convert decision to dictionary for serialization"""
        return {
            "decision_id": self.decision_id,
            "refund_request_id": self.refund_request_id,
            "agent_id": self.agent_id,
            "decision_type": self.decision_type.value,
            "decision_reason": self.decision_reason,
            "status": self.status.value,
            "refund_amount": self.refund_amount.to_dict() if self.refund_amount else None,
            "refund_method": self.refund_method.value if self.refund_method else None,
            "requires_additional_review": self.requires_additional_review,
            "reviewer_agent_id": self.reviewer_agent_id,
            "decision_date": self.decision_date.isoformat(),
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def create_approval(
        cls, 
        refund_request_id: str, 
        agent_id: str, 
        decision_reason: str,
        refund_amount: Money,
        refund_method: RefundMethod
    ) -> 'RefundDecision':
        """Factory method to create an approval decision"""
        decision_id = f"DEC-{uuid4().hex[:8].upper()}"
        return cls(
            decision_id=decision_id,
            refund_request_id=refund_request_id,
            agent_id=agent_id,
            decision_type=DecisionType.APPROVAL,
            decision_reason=decision_reason,
            refund_amount=refund_amount,
            refund_method=refund_method,
            status=DecisionStatus.PENDING_REVIEW
        )

    @classmethod
    def create_rejection(
        cls,
        refund_request_id: str,
        agent_id: str,
        decision_reason: str
    ) -> 'RefundDecision':
        """Factory method to create a rejection decision"""
        decision_id = f"DEC-{uuid4().hex[:8].upper()}"
        return cls(
            decision_id=decision_id,
            refund_request_id=refund_request_id,
            agent_id=agent_id,
            decision_type=DecisionType.REJECTION,
            decision_reason=decision_reason,
            status=DecisionStatus.PENDING_REVIEW
        )

    def __str__(self) -> str:
        return f"RefundDecision {self.decision_id} ({self.decision_type.value})"

    def __repr__(self) -> str:
        return f"<RefundDecision {self.decision_id} type={self.decision_type.value} status={self.status.value}>"