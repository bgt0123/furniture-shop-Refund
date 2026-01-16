from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID
from enum import Enum


class RefundCaseStatus(str, Enum):
    """Refund case status enum."""

    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    COMPLETED = "Completed"


class EligibilityStatus(str, Enum):
    """Refund eligibility status enum."""

    ELIGIBLE = "Eligible"
    PARTIALLY_ELIGIBLE = "Partially Eligible"
    INELIGIBLE = "Ineligible"


class RefundCaseCreate(BaseModel):
    """Schema for creating a refund case."""

    customer_id: UUID
    order_id: str
    products: List[Dict[str, Any]]
    reason: str


from pydantic import ConfigDict


class RefundCaseResponse(BaseModel):
    """Schema for refund case response."""

    id: str
    support_case_id: str
    customer_id: str
    order_id: str
    products: List[Dict[str, Any]]
    total_refund_amount: float
    status: RefundCaseStatus
    eligibility_status: EligibilityStatus
    reason: str
    created_at: datetime
    processed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    agent_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
