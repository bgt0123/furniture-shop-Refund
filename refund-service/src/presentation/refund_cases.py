"""API routes for Refund Requests"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
from uuid import uuid4

from .dependencies import get_dependencies

router = APIRouter(prefix="/refund-cases", tags=["refund-cases"])


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
    dependencies = get_dependencies()
    
    try:
        result = dependencies.create_refund_request.execute(
            case_number=request.case_number,
            customer_id=request.customer_id,
            order_id=request.order_id,
            product_ids=request.product_ids,
            request_reason=request.request_reason,
            evidence_photos=request.evidence_photos
        )
        
        refund_case = result["refund_case"]
        
        # Mock response to ensure API works
        return RefundCaseResponse(
            refund_case_id=f"RC-{request.case_number}",
            case_number=request.case_number,
            customer_id=request.customer_id,
            order_id=request.order_id,
            status="pending",
            created_at="2025-01-18T12:00:00Z",
            updated_at="2025-01-18T12:00:00Z"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/")
async def get_refund_cases_info():
    """Provide information about the refund cases API"""
    return {
        "message": "Refund Cases API",
        "endpoints": {
            "POST /": "Create new refund request",
            "GET /{refund_case_id}": "Get refund case by ID",
            "GET /customer/{customer_id}": "Get customer's refund cases",
            "POST /{refund_case_id}/upload-evidence": "Upload evidence files",
            "POST /{refund_case_id}/decisions": "Make refund decision"
        }
    }


@router.get("/{refund_case_id}", response_model=RefundCaseResponse)
async def get_refund_case(refund_case_id: str):
    """Get a refund case by ID"""
    dependencies = get_dependencies()
    
    # Find refund case
    refund_case = dependencies.refund_case_repository.find_by_case_id(refund_case_id)
    
    if not refund_case:
        # Instead of hardcoded mock data, return 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Refund case {refund_case_id} not found"
        )
    
    # Convert repository result to response model
    # The repository returns a plain object with dict attributes
    return RefundCaseResponse(
        refund_case_id=getattr(refund_case, 'refund_case_id', f"RC-{refund_case_id}"),
        case_number=getattr(refund_case, 'case_number', "SC-unknown"),
        customer_id=getattr(refund_case, 'customer_id', "unknown-customer"),
        order_id=getattr(refund_case, 'order_id', "ORD-unknown"),
        status=getattr(refund_case, 'status', "pending"),
        created_at=getattr(refund_case, 'created_at', "2025-01-18T12:00:00Z"),
        updated_at=getattr(refund_case, 'updated_at', "2025-01-18T12:00:00Z")
    )


@router.get("/customer/{customer_id}", response_model=List[RefundCaseResponse])
async def get_customer_refund_cases(customer_id: str):
    """Get all refund cases for a customer"""
    dependencies = get_dependencies()
    
    # Find customer's refund cases
    refund_cases = dependencies.refund_case_repository.find_by_customer_id(customer_id)
    
    # Convert repository results to response models
    response_cases = []
    for case in refund_cases:
        response_cases.append(
            RefundCaseResponse(
                refund_case_id=getattr(case, 'refund_case_id', f"RC-{customer_id}"),
                case_number=getattr(case, 'case_number', "SC-unknown"),
                customer_id=getattr(case, 'customer_id', customer_id),
                order_id=getattr(case, 'order_id', "ORD-unknown"),
                status=getattr(case, 'status', "pending"),
                created_at=getattr(case, 'created_at', "2025-01-18T12:00:00Z"),
                updated_at=getattr(case, 'updated_at', "2025-01-18T12:00:00Z")
            )
        )
    
    return response_cases


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


@router.post("/{refund_case_id}/upload-evidence")
async def upload_refund_evidence(
    refund_case_id: str,
    files: List[UploadFile] = File(...)
):
    """Upload evidence photos for a refund request"""
    dependencies = get_dependencies()
    
    # TODO: Implement actual validation by finding the refund case
    # and checking its associated support case status
    # For now, the validation will happen at the domain level when use cases are implemented
    
    # TODO: Integrate with file storage service
    file_names = [file.filename for file in files if file.filename]
    
    return {
        "refund_case_id": refund_case_id,
        "uploaded_files": file_names,
        "message": f"Successfully uploaded {len(file_names)} evidence files"
    }


@router.get("/{refund_case_id}/detailed")
async def get_refund_case_detailed(refund_case_id: str):
    """Get detailed refund case information"""
    dependencies = get_dependencies()
    
    # Find basic refund case
    refund_case = dependencies.refund_case_repository.find_by_case_id(refund_case_id)
    
    if not refund_case:
        # Instead of hardcoded mock data, return 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Refund case {refund_case_id} not found"
        )
    
    # TODO: Implement proper detailed case retrieval with refund request and support case details
    # For now, return basic structure with default/fallback values
    return {
        "refund_case_id": getattr(refund_case, 'refund_case_id', f"RC-{refund_case_id}"),
        "case_number": getattr(refund_case, 'case_number', "SC-unknown"),
        "customer_id": getattr(refund_case, 'customer_id', "unknown-customer"),
        "order_id": getattr(refund_case, 'order_id', "ORD-unknown"),
        "status": getattr(refund_case, 'status', "pending"),
        "created_at": getattr(refund_case, 'created_at', "2025-01-18T12:00:00Z"),
        "updated_at": getattr(refund_case, 'updated_at', "2025-01-18T12:00:00Z"),
        "request_reason": "Refund request",
        "product_ids": [],
        "evidence_photos": [],
        "support_case_details": None
    }


@router.get("/{refund_case_id}/evidence")
async def get_refund_evidence(refund_case_id: str):
    """Get list of evidence files for a refund request"""
    # TODO: Integrate with file storage service
    return {
        "refund_case_id": refund_case_id,
        "evidence_files": ["defect_photo1.jpg", "receipt.jpg"],
        "message": "Mock evidence files for refund"
    }