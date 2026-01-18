from datetime import datetime
from typing import List, Optional
from enum import Enum
from uuid import uuid4


class SenderType(Enum):
    """Represents who sent the response"""
    CUSTOMER = "customer"
    AGENT = "agent"


class MessageType(Enum):
    """Represents the type of message"""
    QUESTION = "question"
    ANSWER = "answer"
    STATUS_UPDATE = "status_update"
    CLOSE_CASE = "close_case"


class SupportResponse:
    """Entity representing an individual response within a support case"""

    def __init__(
        self,
        response_id: str,
        case_number: str,
        sender_id: str,
        sender_type: SenderType,
        content: str,
        message_type: MessageType,
        attachments: Optional[List[str]] = None,
        is_internal: bool = False,
        timestamp: Optional[datetime] = None
    ):
        self.response_id = response_id
        self.case_number = case_number
        self.sender_id = sender_id
        self.sender_type = sender_type
        self.content = content
        self.message_type = message_type
        self.attachments = attachments or []
        self.is_internal = is_internal
        self.timestamp = timestamp or datetime.utcnow()

    @property
    def can_customer_see(self) -> bool:
        """Check if this response should be visible to customers"""
        return not self.is_internal

    def __str__(self) -> str:
        return f"Response from {self.sender_type.value} at {self.timestamp}"

    def __repr__(self) -> str:
        return f"<SupportResponse {self.response_id} case={self.case_number} sender={self.sender_type.value}>"