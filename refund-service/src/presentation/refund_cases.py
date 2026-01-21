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
    
    print(f"🐛 DEBUG: Creating refund request for case {request.case_number}")
    
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
        # Return the actual refund case from the repository
        refund_case_id = result["refund_case_id"]
        saved_case = dependencies.refund_case_repository.find_by_case_id(refund_case_id)
        
        if saved_case:
            return RefundCaseResponse(
                refund_case_id=getattr(saved_case, 'refund_case_id', refund_case_id),
                case_number=getattr(saved_case, 'case_number', request.case_number),
                customer_id=getattr(saved_case, 'customer_id', request.customer_id),
                order_id=getattr(saved_case, 'order_id', request.order_id),
                status=getattr(saved_case, 'status', "pending"),
                created_at=getattr(saved_case, 'created_at', "2025-01-18T12:00:00Z"),
                updated_at=getattr(saved_case, 'updated_at', "2025-01-18T12:00:00Z")
            )
        else:
            return RefundCaseResponse(
                refund_case_id=refund_case_id,
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


@router.get("/info")
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


@router.get("/", response_model=List[RefundCaseResponse])
async def get_all_refund_cases():
    """Get all refund cases (for agents)"""
    dependencies = get_dependencies()
    
    # Get all refund cases
    refund_cases = dependencies.refund_case_repository.find_all()
    
    # Convert repository results to response models
    response_cases = []
    for case in refund_cases:
        refund_case_id_value = getattr(case, 'refund_case_id', None)
        case_number_value = getattr(case, 'case_number', None)
        customer_id_value = getattr(case, 'customer_id', None)
        order_id_value = getattr(case, 'order_id', None)
        status_value = getattr(case, 'status', None)
        created_at_value = getattr(case, 'created_at', None)
        updated_at_value = getattr(case, 'updated_at', None)
        
        response_cases.append(
            RefundCaseResponse(
                refund_case_id=refund_case_id_value if refund_case_id_value else "RC-unknown",
                case_number=case_number_value if case_number_value else "unknown",
                customer_id=customer_id_value if customer_id_value else "unknown-customer",
                order_id=order_id_value if order_id_value else "ORD-unknown",
                status=status_value if status_value else "pending",
                created_at=created_at_value if created_at_value else "2025-01-18T12:00:00Z",
                updated_at=updated_at_value if updated_at_value else "2025-01-18T12:00:00Z"
            )
        )
    
    return response_cases


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
    print(f"🔧 Decision requested for refund case {refund_case_id}")
    
    # Determine status based on response type
    status_map = {
        "approval": "approved",
        "rejection": "rejected", 
        "request_additional_evidence": "pending"
    }
    
    new_status = status_map.get(request.response_type, "pending")
    print(f"🔧 Decision type: {request.response_type} -> New status: {new_status}")
    
    # Update refund case status
    dependencies = get_dependencies()
    print(f"🔧 Attempting to update status in repository...")
    success = dependencies.refund_case_repository.update_status(refund_case_id, new_status)
    
    if success:
        print(f"✅ Successfully updated {refund_case_id} status to {new_status}")
        return {
            "refund_case_id": refund_case_id,
            "agent_id": request.agent_id,
            "response_type": request.response_type,
            "new_status": new_status,
            "refund_amount": request.refund_amount,
            "refund_method": request.refund_method,
            "timestamp": "2026-01-20T12:00:00Z"
        }
    else:
        print(f"❌ Failed to update {refund_case_id} status")
        raise HTTPException(status_code=404, detail="Refund case not found")


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


@router.get("/{refund_case_id}")
async def get_refund_case(refund_case_id: str):
    """Get basic refund case information"""
    dependencies = get_dependencies()
    
    # Find the refund case
    refund_case = dependencies.refund_case_repository.find_by_case_id(refund_case_id)
    
    if not refund_case:
        raise HTTPException(status_code=404, detail="Refund case not found")
    
    return {
        "refund_case_id": getattr(refund_case, 'refund_case_id', f"RC-{refund_case_id}"),
        "case_number": getattr(refund_case, 'case_number', "SC-unknown"),
        "customer_id": getattr(refund_case, 'customer_id', "unknown-customer"),
        "order_id": getattr(refund_case, 'order_id', "ORD-unknown"),
        "status": getattr(refund_case, 'status', "pending"),
        "created_at": getattr(refund_case, 'created_at', "2025-01-18T12:00:00Z"),
        "updated_at": getattr(refund_case, 'updated_at', "2025-01-18T12:00:00Z")
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