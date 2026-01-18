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
    """Entity representing a formal response to a refund request decision"""

    def __init__(
        self,
        response_id: str,
        refund_request_id: str,
        agent_id: str,
        response_type: ResponseType,
        response_content: str,
        attachments: Optional[List[str]] = None,
        refund_amount: Optional[str] = None,
        refund_method: Optional[RefundMethod] = None,
        timestamp: Optional[datetime] = None
    ):
        self.response_id = response_id
        self.refund_request_id = refund_request_id
        self.agent_id = agent_id
        self.response_type = response_type
        self.response_content = response_content
        self.attachments = attachments or []
        self.refund_amount = refund_amount
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

    def __str__(self) -> str:
        return f"RefundResponse {self.response_id} ({self.response_type.value})"

    def __repr__(self) -> str:
        return f"<RefundResponse {self.response_id} type={self.response_type.value}>"