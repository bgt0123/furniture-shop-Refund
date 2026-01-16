from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from models.support_case import SupportCaseStatus


class SupportCaseBase(BaseModel):
    """Base support case schema."""

    customer_id: UUID
    order_id: UUID
    products: List[Dict[str, Any]]
    issue_description: str
    attachments: Optional[List[Dict[str, Any]]] = None


class SupportCaseCreate(SupportCaseBase):
    """Schema for creating a support case."""

    pass


class SupportCaseResponse(SupportCaseBase):
    """Schema for support case response."""

    id: UUID
    status: SupportCaseStatus
    created_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
