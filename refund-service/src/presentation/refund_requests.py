"""API routes for Refund Requests"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from uuid import uuid4

router = APIRouter(prefix="/refund-requests", tags=["refund-requests"])


# Pydantic models for request/response
class CreateRefundRequest(BaseModel):
    case_number: str
    customer_id: str
    order_id: str
    product_ids: List[str]
    request_reason: str
    evidence_photos: Optional[List[str]] = None


class RefundCaseResponse(BaseModel):
    refund_case_id: str
    case_number: str
    customer_id: str
    order_id: str
    status: str
    created_at: str
    updated_at: str


class RefundDecisionRequest(BaseModel):
    agent_id: str
    response_type: str  # "approval", "rejection", "request_additional_evidence"
    response_content: str
    refund_amount: Optional[str] = None
    refund_method: Optional[str] = None
    attachments: Optional[List[str]] = None


@router.post("/", response_model=RefundCaseResponse)
async def create_refund_request(request: CreateRefundRequest):
    """Create a new refund request"""
    # Mock implementation
    refund_case_id = f"RC-{uuid4().hex[:8].upper()}"
    
    return RefundCaseResponse(
        refund_case_id=refund_case_id,
        case_number=request.case_number,
        customer_id=request.customer_id,
        order_id=request.order_id,
        status="pending",
        created_at="2025-01-18T12:00:00Z",
        updated_at="2025-01-18T12:00:00Z"
    )


@router.get("/{refund_case_id}", response_model=RefundCaseResponse)
async def get_refund_case(refund_case_id: str):
    """Get a refund case by ID"""
    # Mock implementation
    return RefundCaseResponse(
        refund_case_id=refund_case_id,
        case_number="SC-123456",
        customer_id="cust-123",
        order_id="ORD-789",
        status="pending",
        created_at="2025-01-18T12:00:00Z",
        updated_at="2025-01-18T12:00:00Z"
    )


@router.post("/{refund_case_id}/decisions")
async def make_refund_decision(refund_case_id: str, request: RefundDecisionRequest):
    """Make a decision on a refund request"""
    # Mock implementation
    return {
        "refund_case_id": refund_case_id,
        "agent_id": request.agent_id,
        "response_type": request.response_type,
        "refund_amount": request.refund_amount,
        "refund_method": request.refund_method,
        "timestamp": "2025-01-18T12:00:00Z"
    }