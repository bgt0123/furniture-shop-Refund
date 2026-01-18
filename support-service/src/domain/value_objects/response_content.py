from typing import List, Optional
from enum import Enum


class ResolutionType(Enum):
    """Represents the type of resolution"""
    INFORMATION = "information"
    ACTION_REQUIRED = "action_required"
    CLOSED = "closed"


class ResponseContent:
    """Structured content for support and refund responses"""

    def __init__(
        self,
        body: str,
        title: Optional[str] = None,
        action_items: Optional[List[str]] = None,
        next_steps: Optional[str] = None,
        resolution_type: ResolutionType = ResolutionType.INFORMATION
    ):
        self.title = title
        self.body = body
        self.action_items = action_items or []
        self.next_steps = next_steps
        self.resolution_type = resolution_type

    def __str__(self) -> str:
        if self.title:
            return f"{self.title}: {self.body[:50]}..."
        return f"{self.body[:50]}..."

    def __repr__(self) -> str:
        return f"<ResponseContent {self.resolution_type.value}>"