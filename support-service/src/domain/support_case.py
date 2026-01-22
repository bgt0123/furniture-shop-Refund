from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum
from uuid import uuid4

from .comment import Comment, CommentType


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
    
    A support case manages customer inquiries and refund requests with business rules.
    """

    def __init__(
        self,
        case_number: str,
        customer_id: str,
        case_type: CaseType,
        subject: str,
        description: str,
        refund_request_ids: Optional[List[str]] = None,
        comments: Optional[List[Comment]] = None,
        status: CaseStatus = CaseStatus.OPEN,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        assigned_agent_id: Optional[str] = None,
        order_id: Optional[str] = None,
        product_ids: Optional[List[str]] = None,
        delivery_date: Optional[datetime] = None,
        is_deleted: bool = False
    ):
        self.case_number = case_number
        self.customer_id = customer_id
        self.case_type = case_type
        self.subject = subject
        self.description = description
        self.refund_request_ids = refund_request_ids or []
        self.comments = comments or []
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.assigned_agent_id = assigned_agent_id
        self.order_id = order_id
        self.product_ids = product_ids or []
        self.delivery_date = delivery_date
        self.is_deleted = is_deleted

    def assign_agent(self, agent_id: str) -> None:
        """Assign an agent to the support case"""
        self._ensure_case_not_closed_or_deleted("assign agent to")
        self.assigned_agent_id = agent_id
        self.status = CaseStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()

    def close_case(self) -> None:
        """Close the support case permanently"""
        self._ensure_case_not_deleted("close")
        if self.status == CaseStatus.CLOSED:
            raise ValueError("Support case is already closed")
        self.status = CaseStatus.CLOSED
        self.updated_at = datetime.utcnow()



    def _ensure_case_not_closed_or_deleted(self, operation: str) -> None:
        """Ensure case is not closed or deleted before performing an operation"""
        if self.is_deleted:
            raise ValueError(f"Cannot {operation} a deleted support case")
        if self.status == CaseStatus.CLOSED:
            raise ValueError(f"Cannot {operation} a closed support case")

    def _ensure_case_not_deleted(self, operation: str) -> None:
        """Ensure case is not deleted before performing an operation"""
        if self.is_deleted:
            raise ValueError(f"Cannot {operation} a deleted support case")

    def can_add_refund_request(self) -> bool:
        """Check if refund request can be added"""
        return (
            not self.is_deleted and
            self.status != CaseStatus.CLOSED and
            self.case_type == CaseType.REFUND
        )

    def add_refund_request(self, refund_request_id: str) -> None:
        """Add a refund request to the support case"""
        if not self.can_add_refund_request():
            raise ValueError("Cannot add refund request to this support case")
        
        if refund_request_id in self.refund_request_ids:
            raise ValueError("Refund request already exists in this support case")
        
        self.refund_request_ids.append(refund_request_id)
        self.updated_at = datetime.utcnow()

    def _validate_case_type_transition(self, new_case_type: CaseType) -> None:
        """Validate changing case type"""
        if self.case_type == CaseType.REFUND and new_case_type == CaseType.QUESTION:
            if self.refund_request_ids:
                raise ValueError("Cannot change refund case to question case when refund requests exist")

    def update_case_type(self, case_type: CaseType) -> None:
        """Update the case type"""
        self._ensure_case_not_closed_or_deleted("update case type of")
        self._validate_case_type_transition(case_type)
        self.case_type = case_type
        self.updated_at = datetime.utcnow()

    @property
    def has_active_refund(self) -> bool:
        """Check if there's an active refund request"""
        return len(self.refund_request_ids) > 0

    @property
    def is_closed(self) -> bool:
        """Check if the support case is closed"""
        return self.status == CaseStatus.CLOSED

    def add_comment(
        self,
        author_id: str,
        author_type: str,
        content: str,
        comment_type: CommentType,
        attachments: Optional[List[str]] = None,
        is_internal: bool = False
    ) -> Comment:
        """Add a comment to the support case"""
        self._ensure_case_not_deleted("add comments to")
        
        comment = Comment(
            comment_id=str(uuid4()),
            case_number=self.case_number,
            author_id=author_id,
            author_type=author_type,
            content=content,
            comment_type=comment_type,
            attachments=attachments or [],
            timestamp=datetime.utcnow(),
            is_internal=is_internal
        )
        
        self.comments.append(comment)
        self.updated_at = datetime.utcnow()
        
        return comment

    def add_customer_comment(self, customer_id: str, content: str, attachments: Optional[List[str]] = None) -> Comment:
        """Add a customer comment to the support case"""
        return self.add_comment(
            author_id=customer_id,
            author_type="customer",
            content=content,
            comment_type=CommentType.CUSTOMER_COMMENT,
            attachments=attachments
        )

    def add_agent_response(self, agent_id: str, content: str, attachments: Optional[List[str]] = None,
                         is_internal: bool = False) -> Comment:
        """Add an agent response to the support case"""
        return self.add_comment(
            author_id=agent_id,
            author_type="agent",
            content=content,
            comment_type=CommentType.AGENT_RESPONSE,
            attachments=attachments,
            is_internal=is_internal
        )

    def add_refund_feedback(
        self, 
        refund_service_id: str, 
        content: str, 
        attachments: Optional[List[str]] = None,
        is_internal: bool = False
    ) -> Comment:
        """Add refund feedback from refund service"""
        return self.add_comment(
            author_id=refund_service_id,
            author_type="refund_service",
            content=content,
            comment_type=CommentType.REFUND_FEEDBACK,
            attachments=attachments,
            is_internal=is_internal
        )

    def get_case_history(self, user_role: str = "customer"):
        """Get all case history events for the specified user role"""
        from .value_objects.case_history import CaseHistory, TimelineEventType
        history_events = []
        
        # Add case creation event
        creation_event = CaseHistory.create_system_event(
            event_type=TimelineEventType.CASE_CREATED,
            content=f"Support case #{self.case_number} created",
            case_number=self.case_number,
            metadata={"customer_id": self.customer_id, "case_type": self.case_type.value}
        )
        history_events.append(creation_event)
        
        # Add comments as history events
        for comment in self.comments:
            history_event = CaseHistory.from_comment(comment)
            
            # Filter by visibility based on user role
            if user_role == "customer" and history_event.is_visible_to_customer():
                history_events.append(history_event)
            elif user_role == "agent" and history_event.is_visible_to_agent():
                history_events.append(history_event)
        
        # Add case closure event if closed
        if self.status == CaseStatus.CLOSED:
            closure_event = CaseHistory.create_system_event(
                event_type=TimelineEventType.CASE_CLOSED,
                content=f"Support case #{self.case_number} closed",
                case_number=self.case_number
            )
            history_events.append(closure_event)
        
        # Sort by timestamp
        return sorted(history_events, key=lambda e: e.timestamp)

    def get_visible_comments(self) -> List[Comment]:
        """Get comments that should be visible in case timeline"""
        return [comment for comment in self.comments if not comment.is_internal]

    def merge_comment_systems(self, existing_comments: List['Comment']) -> None:
        """Merge existing comment system into this domain model"""
        self.comments.extend(existing_comments)

    def to_dict(self, include_history: bool = False, user_role: str = "customer") -> dict:
        """Convert support case to dictionary for serialization
        
        Args:
            include_history: Whether to include structured case history instead of raw comments
            user_role: Role of user requesting the data ("customer" or "agent")
        """
        base_data = {
            "case_number": self.case_number,
            "customer_id": self.customer_id,
            "case_type": self.case_type.value,
            "subject": self.subject,
            "description": self.description,
            "refund_request_ids": self.refund_request_ids,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "assigned_agent_id": self.assigned_agent_id,
            "order_id": self.order_id,
            "product_ids": self.product_ids,
            "delivery_date": self.delivery_date.isoformat() if self.delivery_date else None,
            "is_deleted": self.is_deleted
        }
        
        if include_history:
            # Include structured case history
            from .value_objects.case_history import CaseHistory
            base_data["case_history"] = [
                event.to_dict() for event in self.get_case_history(user_role)
            ]
        else:
            # Backward compatibility: include raw comments
            base_data["comments"] = [c.to_dict() for c in self.comments]
            
        return base_data

    def __str__(self) -> str:
        return f"SupportCase {self.case_number} ({self.status.value})"

    def __repr__(self) -> str:
        return f"<SupportCase {self.case_number} customer={self.customer_id} type={self.case_type.value}>"