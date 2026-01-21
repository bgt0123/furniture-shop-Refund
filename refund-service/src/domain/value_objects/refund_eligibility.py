from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class RefundEligibility:
    """Value object representing refund eligibility determination"""
    is_eligible: bool
    reasons: list[str]
    calculated_refund_amount: Optional[Decimal] = None
    eligibility_date: Optional[datetime] = None

    def __post_init__(self):
        """Validate the eligibility object"""
        if not isinstance(self.is_eligible, bool):
            raise TypeError("is_eligible must be a boolean")
        if not isinstance(self.reasons, list):
            raise TypeError("reasons must be a list")

    @property
    def primary_reason(self) -> str:
        """Get the primary reason for eligibility determination"""
        return self.reasons[0] if self.reasons else "Unknown"

    def can_calculate_amount(self) -> bool:
        """Check if refund amount can be calculated"""
        return self.is_eligible and self.calculated_refund_amount is not None

    def get_formatted_amount(self) -> str:
        """Get formatted refund amount for display"""
        if self.calculated_refund_amount:
            return f"${self.calculated_refund_amount:,.2f}"
        return "Not calculated"

    def to_dict(self) -> dict:
        """Convert eligibility to dictionary for serialization"""
        return {
            "is_eligible": self.is_eligible,
            "reasons": self.reasons,
            "calculated_refund_amount": float(self.calculated_refund_amount) if self.calculated_refund_amount else None,
            "eligibility_date": self.eligibility_date.isoformat() if self.eligibility_date else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RefundEligibility':
        """Create eligibility from dictionary"""
        calculated_amount = None
        if data.get("calculated_refund_amount"):
            calculated_amount = Decimal(str(data["calculated_refund_amount"]))
            
        return cls(
            is_eligible=data["is_eligible"],
            reasons=data["reasons"],
            calculated_refund_amount=calculated_amount,
            eligibility_date=datetime.fromisoformat(data["eligibility_date"]) if data.get("eligibility_date") else None
        )

    def __str__(self) -> str:
        status = "✅ Eligible" if self.is_eligible else "❌ Ineligible"
        return f"RefundEligibility({status}: {self.primary_reason})"

    def __repr__(self) -> str:
        return f"<RefundEligibility eligible={self.is_eligible} reasons={len(self.reasons)} amount={self.calculated_refund_amount}>"