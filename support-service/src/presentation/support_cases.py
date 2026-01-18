"""API routes for Support Cases"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from uuid import uuid4

router = APIRouter(prefix="/support-cases", tags=["support-cases"])


# Pydantic models for request/response
class CreateSupportCaseRequest(BaseModel):
    customer_id: str
    case_type: str  # "question" or "refund"
    subject: str
    description: str
    refund_request_id: Optional[str] = None


class SupportCaseResponse(BaseModel):
    case_number: str
    customer_id: str
    case_type: str
    subject: str
    description: str
    status: str
    refund_request_id: Optional[str] = None
    assigned_agent_id: Optional[str] = None
    created_at: str
    updated_at: str


class SupportResponseRequest(BaseModel):
    sender_id: str
    sender_type: str  # "customer" or "agent"
    content: str
    message_type: str  # "question", "answer", "status_update", "close_case"
    attachments: Optional[List[str]] = None
    is_internal: bool = False


@router.post("/", response_model=SupportCaseResponse)
async def create_support_case(request: CreateSupportCaseRequest):
    """Create a new support case"""
    # In a real implementation, this would:
    # 1. Validate the request
    # 2. Create the SupportCase aggregate
    # 3. Save to database
    # 4. Return the created case
    
    case_number = f"SC-{uuid4().hex[:8].upper()}"
    
    return SupportCaseResponse(
        case_number=case_number,
        customer_id=request.customer_id,
        case_type=request.case_type,
        subject=request.subject,
        description=request.description,
        status="open",
        refund_request_id=request.refund_request_id,
        created_at="2025-01-18T12:00:00Z",
        updated_at="2025-01-18T12:00:00Z"
    )


@router.get("/{case_number}", response_model=SupportCaseResponse)
async def get_support_case(case_number: str):
    """Get a support case by ID"""
    # Mock implementation
    return SupportCaseResponse(
        case_number=case_number,
        customer_id="cust-123",
        case_type="question",
        subject="Test case",
        description="Test description",
        status="open",
        created_at="2025-01-18T12:00:00Z",
        updated_at="2025-01-18T12:00:00Z"
    )


@router.post("/{case_number}/responses")
async def add_response(case_number: str, request: SupportResponseRequest):
    """Add a response to a support case"""
    # Mock implementation
    return {
        "response_id": str(uuid4()),
        "case_number": case_number,
        "sender_id": request.sender_id,
        "sender_type": request.sender_type,
        "content": request.content,
        "timestamp": "2025-01-18T12:00:00Z"
    }


@router.put("/{case_number}/assign/{agent_id}")
async def assign_agent(case_number: str, agent_id: str):
    """Assign an agent to a support case"""
    # Mock implementation
    return {
        "case_number": case_number,
        "assigned_agent_id": agent_id,
        "status": "in_progress",
        "updated_at": "2025-01-18T12:00:00Z"
    }


@router.put("/{case_number}/close")
async def close_case(case_number: str):
    """Close a support case"""
    # Mock implementation
    return {
        "case_number": case_number,
        "status": "closed",
        "updated_at": "2025-01-18T12:00:00Z"
    }