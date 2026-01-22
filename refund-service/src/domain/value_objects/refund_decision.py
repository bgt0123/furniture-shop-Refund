from enum import Enum
from dataclasses import dataclass


class RefundDecisionValue(Enum):
    """Value object representing possible refund decisions"""
    ACCEPTED = "accepted"
    REJECTED = "rejected" 
    NEED_MORE_INPUT = "need_more_input"


@dataclass(frozen=True)
class RefundDecision:
    """Value object representing a refund decision with reason/description"""
    decision: RefundDecisionValue
    reason: str

    def display(self) -> str:
        """Display the decision in a user-friendly format"""
        if self.decision == RefundDecisionValue.ACCEPTED:
            return "Accepted"
        elif self.decision == RefundDecisionValue.REJECTED:
            return "Rejected"
        elif self.decision == RefundDecisionValue.NEED_MORE_INPUT:
            return "Need More Input"
        else:
            return "Unknown"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "decision": self.decision.value,
            "reason": self.reason,
            "display": self.display()
        }

    @classmethod
    def from_string(cls, decision_str: str, reason: str = "") -> 'RefundDecision':
        """Create from string representation"""
        try:
            decision_value = RefundDecisionValue(decision_str.lower())
            return cls(decision_value, reason)
        except ValueError:
            # Handle legacy decision types and provide fallbacks
            decision_lower = decision_str.lower()
            if decision_lower in ["approval", "approved", "accept", "accepted"]:
                return cls(RefundDecisionValue.ACCEPTED, reason)
            elif decision_lower in ["rejection", "rejected", "deny", "rejected"]:
                return cls(RefundDecisionValue.REJECTED, reason)
            elif decision_lower in ["request_additional_evidence", "need_more_info", "request_more_info", "need_more_input"]:
                return cls(RefundDecisionValue.NEED_MORE_INPUT, reason)
            else:
                # Default to rejected for unknown values
                return cls(RefundDecisionValue.REJECTED, f"Unknown decision type '{decision_str}': {reason}")

    def __str__(self) -> str:
        return f"{self.display()}: {self.reason}"

    def __repr__(self) -> str:
        return f"RefundDecision({self.decision.value}, {repr(self.reason)})"