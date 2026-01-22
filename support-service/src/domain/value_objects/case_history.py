"""CaseHistory value object representing timeline events visible in frontend"""

from datetime import datetime
from typing import List, Optional
from enum import Enum


class TimelineEventType(Enum):
    """Types of events that appear in case history"""
    CUSTOMER_COMMENT = "customer_comment"
    AGENT_RESPONSE = "agent_response" 
    REFUND_FEEDBACK = "refund_feedback"
    CASE_CREATED = "case_created"
    CASE_CLOSED = "case_closed"
    CASE_REOPENED = "case_reopened"
    AGENT_ASSIGNED = "agent_assigned"


class CaseHistory:
    """Value object representing a timeline event in case history"""
    
    def __init__(
        self,
        event_id: str,
        event_type: TimelineEventType,
        timestamp: datetime,
        author_id: str,
        author_type: str,
        content: str,
        actor: Optional[str] = None,
        is_internal: bool = False,
        attachments: Optional[List[str]] = None,
        metadata: Optional[dict] = None
    ):
        self.event_id = event_id
        self.event_type = event_type
        self.timestamp = timestamp
        self.author_id = author_id
        self.author_type = author_type
        self.content = content
        self.actor = actor or author_id
        self.is_internal = is_internal
        self.attachments = attachments or []
        self.metadata = metadata or {}
    
    def is_visible_to_customer(self) -> bool:
        """Check if this event should be visible to customers"""
        return not self.is_internal and self.event_type != TimelineEventType.REFUND_FEEDBACK
    
    def is_visible_to_agent(self) -> bool:
        """Check if this event should be visible to agents"""
        return True  # Agents can see all events
    
    def has_attachments(self) -> bool:
        """Check if event has attachments"""
        return len(self.attachments) > 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API response"""
        result = {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "author_id": self.author_id,
            "author_type": self.author_type,
            "content": self.content,
            "actor": self.actor,
            "is_internal": self.is_internal,
            "attachments": self.attachments,
        }
        
        # Add metadata fields directly if present
        if self.metadata:
            result.update(self.metadata)
            
        return result
    
    @classmethod
    def from_comment(cls, comment) -> 'CaseHistory':
        """Create CaseHistory from Comment domain object"""
        event_type_map = {
            "customer_comment": TimelineEventType.CUSTOMER_COMMENT,
            "agent_response": TimelineEventType.AGENT_RESPONSE,
            "refund_feedback": TimelineEventType.REFUND_FEEDBACK
        }
        
        event_type = event_type_map.get(
            comment.comment_type.value if hasattr(comment.comment_type, 'value') else comment.comment_type,
            TimelineEventType.CUSTOMER_COMMENT
        )
        
        return cls(
            event_id=comment.comment_id,
            event_type=event_type,
            timestamp=comment.timestamp,
            author_id=comment.author_id,
            author_type=comment.author_type,
            content=comment.content,
            is_internal=comment.is_internal,
            attachments=comment.attachments
        )
    
    @classmethod
    def create_system_event(
        cls,
        event_type: TimelineEventType,
        content: str,
        case_number: str,
        metadata: Optional[dict] = None
    ) -> 'CaseHistory':
        """Create system-generated timeline event"""
        event_id = f"SYS-{case_number}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        base_data = {
            "event_id": event_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow(),
            "author_id": "system",
            "author_type": "system",
            "content": content,
            "actor": "System",
            "is_internal": False,
            "attachments": [],
            "metadata": metadata or {}
        }
        
        return cls(**base_data)
    
    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.event_type.value}: {self.content}"
    
    def __repr__(self) -> str:
        return f"<CaseHistory {self.event_id} type={self.event_type.value}>"