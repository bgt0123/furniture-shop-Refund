from datetime import datetime
from typing import List, Optional
from enum import Enum
from uuid import uuid4

from .support_response import SupportResponse, SenderType, MessageType


class CaseStatus(Enum):
    """Represents the status of a support case"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class CaseType(Enum):
    """Represents the type of support case"""
    QUESTION = "question"
    REFUND = "refund"


class SupportCase:
    """Aggregate root for support cases
    
    A support case represents a customer inquiry that may contain
    refund requests. This aggregate ensures business rules are enforced.
    """

    def __init__(
        self,
        case_number: str,
        customer_id: str,
        case_type: CaseType,
        subject: str,
        description: str,
        refund_request_id: Optional[str] = None,
        support_responses: Optional[List[SupportResponse]] = None,
        status: CaseStatus = CaseStatus.OPEN,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        assigned_agent_id: Optional[str] = None
    ):
        self.case_number = case_number
        self.customer_id = customer_id
        self.case_type = case_type
        self.subject = subject
        self.description = description
        self.refund_request_id = refund_request_id
        self.support_responses = support_responses or []
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.assigned_agent_id = assigned_agent_id

    def add_response(
        self,
        sender_id: str,
        sender_type: SenderType,
        content: str,
        message_type: MessageType,
        attachments: Optional[List[str]] = None,
        is_internal: bool = False
    ) -> SupportResponse:
        """Add a response to the support case"""
        
        response = SupportResponse(
            response_id=str(uuid4()),
            case_number=self.case_number,
            sender_id=sender_id,
            sender_type=sender_type,
            content=content,
            message_type=message_type,
            attachments=attachments or [],
            is_internal=is_internal
        )
        
        self.support_responses.append(response)
        self.updated_at = datetime.utcnow()
        
        return response

    def assign_agent(self, agent_id: str) -> None:
        """Assign an agent to the support case"""
        self.assigned_agent_id = agent_id
        self.status = CaseStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()

    def close_case(self) -> None:
        """Close the support case"""
        self.status = CaseStatus.CLOSED
        self.updated_at = datetime.utcnow()

    def add_refund_request(self, refund_request_id: str) -> None:
        """Add a refund request to the support case"""
        if self.case_type != CaseType.REFUND:
            raise ValueError("Cannot add refund request to non-refund case")
        
        if self.refund_request_id:
            raise ValueError("Support case already has a refund request")
        
        self.refund_request_id = refund_request_id
        self.updated_at = datetime.utcnow()

    @property
    def can_customer_access(self) -> bool:
        """Check if customer should have access to this case"""
        # Customers can only access their own cases
        return self.customer_id.startswith("customer")

    def __str__(self) -> str:
        return f"SupportCase {self.case_number} ({self.status.value})"

    def __repr__(self) -> str:
        return f"<SupportCase {self.case_number} customer={self.customer_id} type={self.case_type.value}>"