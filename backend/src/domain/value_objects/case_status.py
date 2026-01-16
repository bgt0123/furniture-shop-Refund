"""Case status value objects."""

from enum import Enum


class CaseStatus(Enum):
    """Support case status enumeration."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

    def can_transition_to(self, new_status: "CaseStatus") -> bool:
        """Check if status transition is valid."""
        valid_transitions = {
            self.OPEN: [self.IN_PROGRESS, self.RESOLVED, self.CLOSED],
            self.IN_PROGRESS: [self.RESOLVED, self.CLOSED],
            self.RESOLVED: [self.CLOSED],
            self.CLOSED: [],
        }
        return new_status in valid_transitions.get(self, [])
