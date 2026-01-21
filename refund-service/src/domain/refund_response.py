from datetime import datetime
from typing import List, Optional
from enum import Enum
from uuid import uuid4
from .value_objects.money import Money


class ResponseType(Enum):
    """Represents the type of refund response"""
    APPROVAL = "approval"
    REJECTION = "rejection"
    REQUEST_ADDITIONAL_EVIDENCE = "request_additional_evidence"


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
        response_type: ResponseType,
        response_content: str,
        refund_amount: Optional[Money] = None,
        attachments: Optional[List[str]] = None,
        refund_method: Optional[RefundMethod] = None,
        timestamp: Optional[datetime] = None
    ):
        if response_type == ResponseType.APPROVAL and refund_amount is None:
            raise ValueError("Approval responses must include refund amount")
        if response_type == ResponseType.APPROVAL and refund_method is None:
            raise ValueError("Approval responses must include refund method")
            
        self.response_id = response_id
        self.refund_request_id = refund_request_id
        self.agent_id = agent_id
        self.response_type = response_type
        self.response_content = response_content
        self.refund_amount = refund_amount
        self.attachments = attachments or []
        self.refund_method = refund_method
        self.timestamp = timestamp or datetime.utcnow()

    @property
    def is_approval(self) -> bool:
        """Check if this response is an approval"""
        return self.response_type == ResponseType.APPROVAL

    @property
    def is_rejection(self) -> bool:
        """Check if this response is a rejection"""
        return self.response_type == ResponseType.REJECTION

    def get_refund_amount_display(self) -> str:
        """Get formatted refund amount for display"""
        return str(self.refund_amount) if self.refund_amount else "N/A"

    def to_dict(self) -> dict:
        """Convert response to dictionary for serialization"""
        return {
            "response_id": self.response_id,
            "refund_request_id": self.refund_request_id,
            "agent_id": self.agent_id,
            "response_type": self.response_type.value,
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
            
        return cls(
            response_id=data["response_id"],
            refund_request_id=data["refund_request_id"],
            agent_id=data["agent_id"],
            response_type=ResponseType(data["response_type"]),
            response_content=data["response_content"],
            refund_amount=refund_amount,
            attachments=data.get("attachments", []),
            refund_method=refund_method,
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None
        )

    def __str__(self) -> str:
        return f"RefundResponse {self.response_id} ({self.response_type.value})"

    def __repr__(self) -> str:
        return f"<RefundResponse {self.response_id} type={self.response_type.value} amount={self.refund_amount}>"