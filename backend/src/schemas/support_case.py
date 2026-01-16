from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from enum import Enum


class SupportCaseStatus(str, Enum):
    """Support case status enum."""

    OPEN = "Open"
    CLOSED = "Closed"


class RefundIntention(str, Enum):
    """Refund intention enum."""

    YES = "Yes"
    NO = "No"


class SupportCaseBase(BaseModel):
    """Base support case schema."""

    customer_id: UUID
    order_id: str
    products: List[Dict[str, Any]]
    issue_description: str
    attachments: Optional[List[Dict[str, Any]]] = None
    intends_refund: RefundIntention = RefundIntention.NO


class SupportCaseCreate(SupportCaseBase):
    """Schema for creating a support case."""

    pass


class SupportCaseResponse(SupportCaseBase):
    """Schema for support case response."""

    id: UUID
    status: SupportCaseStatus
    created_at: datetime
    closed_at: Optional[datetime] = None
    intends_refund: RefundIntention = RefundIntention.NO

    model_config = ConfigDict(from_attributes=True)
