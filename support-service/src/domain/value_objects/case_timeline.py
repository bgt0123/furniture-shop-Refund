from datetime import datetime
from typing import Optional


class CaseTimeline:
    """Value object to track status changes and updates"""

    def __init__(
        self,
        timestamp: Optional[datetime] = None,
        status: Optional[str] = None,
        actor: Optional[str] = None,
        notes: Optional[str] = None
    ):
        self.timestamp = timestamp or datetime.utcnow()
        self.status = status
        self.actor = actor
        self.notes = notes

    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.status} by {self.actor}"

    def __repr__(self) -> str:
        return f"<CaseTimeline {self.status} @ {self.timestamp}>"