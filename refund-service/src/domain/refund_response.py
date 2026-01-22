from datetime import datetime
from typing import List, Optional
from enum import Enum
from uuid import uuid4
from .value_objects.money import Money
from .value_objects.refund_decision import RefundDecision, RefundDecisionValue





class RefundMethod(Enum):
    """Represents refund delivery methods"""
    MONEY = "money"
    VOUCHER = "voucher"
    REPLACEMENT = "replacement"


class RefundResponse:
    """Aggregate representing a formal response to a refund request decision"""

    def __init__(
        self,
        response_id: str,
        refund_request_id: str,
        agent_id: str,
        decision: RefundDecision,
        response_content: str,
        refund_amount: Optional[Money] = None,
        attachments: Optional[List[str]] = None,
        refund_method: Optional[RefundMethod] = None,
        timestamp: Optional[datetime] = None
    ):
        if decision.decision == RefundDecisionValue.ACCEPTED and refund_amount is None:
            raise ValueError("Accepted responses must include refund amount")
        if decision.decision == RefundDecisionValue.ACCEPTED and refund_method is None:
            raise ValueError("Accepted responses must include refund method")
            
        self.response_id = response_id
        self.refund_request_id = refund_request_id
        self.agent_id = agent_id
        self.decision = decision
        self.response_content = response_content
        self.refund_amount = refund_amount
        self.attachments = attachments or []
        self.refund_method = refund_method
        self.timestamp = timestamp or datetime.utcnow()

    @property
    def is_approval(self) -> bool:
        """Check if this response is an approval"""
        return self.decision.decision == RefundDecisionValue.ACCEPTED

    @property
    def is_rejection(self) -> bool:
        """Check if this response is a rejection"""
        return self.decision.decision == RefundDecisionValue.REJECTED

    def get_refund_amount_display(self) -> str:
        """Get formatted refund amount for display"""
        return str(self.refund_amount) if self.refund_amount else "N/A"

    def to_dict(self) -> dict:
        """Convert response to dictionary for serialization"""
        return {
            "response_id": self.response_id,
            "refund_request_id": self.refund_request_id,
            "agent_id": self.agent_id,
            "decision": self.decision.to_dict(),
            "response_content": self.response_content,
            "refund_amount": self.refund_amount.to_dict() if self.refund_amount else None,
            "attachments": self.attachments,
            "refund_method": self.refund_method.value if self.refund_method else None,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RefundResponse':
        """Create response from dictionary"""
        refund_amount_data = data.get("refund_amount")
        refund_amount = Money.from_dict(refund_amount_data) if refund_amount_data else None
        
        refund_method = None
        if data.get("refund_method"):
            refund_method = RefundMethod(data["refund_method"])
        
        # Handle legacy data format
        decision_data = data.get("decision")
        if decision_data:
            decision = RefundDecision.from_string(decision_data.get("decision"))
        else:
            # Fallback for legacy response_type format
            decision = RefundDecision.from_string(data["response_type"])
            
        return cls(
            response_id=data["response_id"],
            refund_request_id=data["refund_request_id"],
            agent_id=data["agent_id"],
            decision=decision,
            response_content=data["response_content"],
            refund_amount=refund_amount,
            attachments=data.get("attachments", []),
            refund_method=refund_method,
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None
        )

    def __str__(self) -> str:
        return f"RefundResponse {self.response_id} ({self.decision.display()})"

    def __repr__(self) -> str:
        return f"<RefundResponse {self.response_id} decision={self.decision} amount={self.refund_amount}>"