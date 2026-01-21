from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from enum import Enum


class CommentType(Enum):
    """Represents the type of comment"""
    CUSTOMER_COMMENT = "customer_comment"
    AGENT_RESPONSE = "agent_response"
    REFUND_FEEDBACK = "refund_feedback"


class Comment:
    """Entity representing a comment within a support case
    
    Comments can be made by customers, agents, or refund feedback from refund service"""

    def __init__(
        self,
        comment_id: str,
        case_number: str,
        author_id: str,
        author_type: str,  # "customer", "agent", "refund_service"
        content: str,
        comment_type: CommentType,
        attachments: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None,
        is_internal: bool = False
    ):
        self.comment_id = comment_id
        self.case_number = case_number
        self.author_id = author_id
        self.author_type = author_type
        self.content = content
        self.comment_type = comment_type
        self.attachments = attachments or []
        self.timestamp = timestamp or datetime.utcnow()
        self.is_internal = is_internal

    def is_agent_response(self) -> bool:
        """Check if this comment is from an agent"""
        return self.author_type == "agent" and self.comment_type == CommentType.AGENT_RESPONSE

    def is_customer_comment(self) -> bool:
        """Check if this comment is from a customer"""
        return self.author_type == "customer" and self.comment_type == CommentType.CUSTOMER_COMMENT

    def is_refund_feedback(self) -> bool:
        """Check if this comment is refund feedback"""
        return self.author_type == "refund_service" and self.comment_type == CommentType.REFUND_FEEDBACK

    def can_customer_see(self) -> bool:
        """Check if this comment should be visible to customers"""
        return (
            self.is_customer_comment() or 
            self.is_agent_response() or 
            (self.is_refund_feedback() and not self.is_internal)
        )

    def __str__(self) -> str:
        return f"Comment by {self.author_type} at {self.timestamp}"

    def __repr__(self) -> str:
        return f"<Comment {self.comment_id} case={self.case_number} type={self.comment_type.value}>"