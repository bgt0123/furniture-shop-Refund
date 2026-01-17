from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from .refund_case import RefundCaseResponse


class RefundCaseApproval(BaseModel):
    """Schema for refund case approval."""

    approval_notes: Optional[str] = None


class RefundCaseRejection(BaseModel):
    """Schema for refund case rejection."""

    reason: str


class RefundCaseAdminList(BaseModel):
    """Schema for listing refund cases in admin view."""

    id: UUID
    support_case_id: UUID
    customer_id: UUID
    customer_name: str
    customer_email: str
    order_id: UUID
    status: str
    eligibility_status: str
    total_refund_amount: float
    created_at: datetime

    class Config:
        orm_mode = True


class AgentRefundListResponse(BaseModel):
    """Response schema for agent refund list with pagination."""

    refund_cases: List[RefundCaseAdminList]
    total_count: int
    limit: int
    offset: int
