"""Refund status value objects."""

from enum import Enum


class RefundStatus(Enum):
    """Refund case status enumeration."""

    PENDING = "pending"
    APPROVED = "approved"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    def can_transition_to(self, new_status: "RefundStatus") -> bool:
        """Check if status transition is valid."""
        valid_transitions = {
            self.PENDING: [self.APPROVED, self.CANCELLED],
            self.APPROVED: [self.EXECUTED, self.FAILED],
            self.EXECUTED: [],
            self.FAILED: [self.APPROVED],
            self.CANCELLED: [],
        }
        return new_status in valid_transitions.get(self, [])
