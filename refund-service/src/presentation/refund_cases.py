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
    refund_case_id: str  # This maps to refund_request_id from repository
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
            support_case_number=request.case_number,
            customer_id=request.customer_id,
            order_id=request.order_id,
            product_ids=request.product_ids,
            request_reason=request.request_reason,
            evidence_photos=request.evidence_photos
        )
        
        refund_request_id = result["refund_request_id"]
        
        # Update support case with the refund request ID
        await update_support_case_with_refund_request(request.case_number, refund_request_id)
        
        # Return the actual refund case from the repository
        saved_case = dependencies.refund_request_repository.find_by_id(refund_request_id)
        
        if saved_case:
            # Handle status enum conversion
            status_obj = getattr(saved_case, 'status', None)
            status_str = "pending"
            if status_obj:
                if hasattr(status_obj, 'value'):
                    status_str = status_obj.value
                else:
                    status_str = str(status_obj)
            
            created_at_obj = getattr(saved_case, 'created_at', None)
            created_at_str = "2025-01-18T12:00:00Z"
            if created_at_obj:
                if hasattr(created_at_obj, 'isoformat'):
                    created_at_str = created_at_obj.isoformat()
                else:
                    created_at_str = str(created_at_obj)
            
            return RefundCaseResponse(
                refund_case_id=refund_request_id,
                case_number=getattr(saved_case, 'case_number', request.case_number),
                customer_id=getattr(saved_case, 'customer_id', request.customer_id),
                order_id=getattr(saved_case, 'order_id', request.order_id),
                status=status_str,
                created_at=created_at_str,
                updated_at=getattr(saved_case, 'updated_at', "2025-01-18T12:00:00Z")
            )
        else:
            return RefundCaseResponse(
                refund_case_id=refund_request_id,
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
    refund_cases = dependencies.refund_request_repository.find_all()
    
    # Convert repository results to response models
    response_cases = []
    for case in refund_cases:
        # Extract values directly from RefundRequest object using getattr
        # to avoid issues with to_dict() method
        refund_case_id = getattr(case, 'refund_request_id', "RC-unknown")
        support_case_number = getattr(case, 'support_case_number', "unknown")
        customer_id = getattr(case, 'customer_id', "unknown-customer")
        
        # Use first product as order_id
        product_ids = getattr(case, 'product_ids', [])
        order_id = product_ids[0] if product_ids else "ORD-unknown"
        
        # Handle status enum
        status_val = getattr(case, 'status', None)
        status_str = "pending"
        if status_val:
            if hasattr(status_val, 'value'):
                status_str = status_val.value
            else:
                status_str = str(status_val)
        
        # Get created_at safely
        created_at_val = getattr(case, 'created_at', None)
        if created_at_val and hasattr(created_at_val, 'isoformat'):
            created_at_str = created_at_val.isoformat()
        else:
            created_at_str = str(created_at_val) if created_at_val else "2025-01-18T12:00:00Z"
        
        response_cases.append(
            RefundCaseResponse(
                refund_case_id=refund_case_id,
                case_number=support_case_number,
                customer_id=customer_id,
                order_id=order_id,
                status=status_str,
                created_at=created_at_str,
                updated_at="2025-01-18T12:00:00Z"
            )
        )
    
    return response_cases


@router.get("/customer/{customer_id}", response_model=List[RefundCaseResponse])
async def get_customer_refund_cases(customer_id: str):
    """Get all refund cases for a customer"""
    dependencies = get_dependencies()
    
    # Find customer's refund cases
    refund_cases = dependencies.refund_request_repository.find_by_customer_id(customer_id)
    
    # Convert repository results to response models
    response_cases = []
    for case in refund_cases:
        case_number = getattr(case, 'support_case_number', None)
        if not case_number:
            case_number = getattr(case, 'case_number', None)
        
        # Use refund_request_id as refund_case_id to match frontend expectations
        refund_case_id = getattr(case, 'refund_request_id', None)
        if not refund_case_id:
            refund_case_id = getattr(case, 'refund_case_id', f"RC-{customer_id}")
        
        # Handle status enum conversion
        status_obj = getattr(case, 'status', None)
        status_str = "pending"
        if status_obj:
            if hasattr(status_obj, 'value'):
                status_str = status_obj.value
            else:
                status_str = str(status_obj)
        
        response_cases.append(
            RefundCaseResponse(
                refund_case_id=refund_case_id if refund_case_id else f"RC-{customer_id}",
                case_number=case_number if case_number else "SC-unknown",
                customer_id=getattr(case, 'customer_id', customer_id),
                order_id=getattr(case, 'order_id', "ORD-unknown"),
                status=status_str,
                created_at=getattr(case, 'created_at', "2025-01-18T12:00:00Z"),
                updated_at=getattr(case, 'updated_at', "2025-01-18T12:00:00Z")
            )
        )
    
    return response_cases


@router.post("/{refund_request_id}/decisions")
async def make_refund_decision(refund_request_id: str, request: RefundDecisionRequest):
    """Make a decision on a refund request using DDD aggregates"""
    print(f"Ⓡ Decision requested for refund request {refund_request_id}")
    
    dependencies = get_dependencies()
    
    # Find the refund request
    refund_request = dependencies.refund_request_repository.find_by_id(refund_request_id)
    if not refund_request:
        raise HTTPException(status_code=404, detail="Refund request not found")
    
    # Convert response type enum
    from domain.refund_response import ResponseType
    try:
        response_type = ResponseType(request.response_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid response type: {request.response_type}")
    
    # Create refund response
    from domain.refund_response import RefundResponse, RefundMethod
    from domain.value_objects.money import Money
    
    refund_amount = None
    refund_method = None
    if request.refund_amount:
        refund_amount = Money.from_dict({"amount": float(request.refund_amount), "currency": "USD"})
    if request.refund_method:
        refund_method = RefundMethod(request.refund_method)
    
    response = RefundResponse(
        response_id=f"RESP-{refund_request_id}",
        refund_request_id=refund_request_id,
        agent_id=request.agent_id,
        response_type=response_type,
        response_content=request.response_content,
        refund_amount=refund_amount,
        refund_method=refund_method,
        attachments=request.attachments or []
    )
    
    # Apply decision to refund request
    if response_type == ResponseType.APPROVAL:
        if not refund_amount:
            raise HTTPException(status_code=400, detail="Refund amount is required for approvals")
        refund_request.approve(request.agent_id, request.response_content, refund_amount)
    elif response_type == ResponseType.REJECTION:
        refund_request.reject(request.agent_id, request.response_content)
    elif response_type == ResponseType.REQUEST_ADDITIONAL_EVIDENCE:
        refund_request.request_additional_evidence(request.agent_id, request.response_content)
    
    # Save updated refund request
    dependencies.refund_request_repository.save(refund_request)
    
    # Notify support service about refund decision
    await notify_support_service(refund_request, response)
    
    print(f"✅ Successfully processed refund decision for {refund_request_id}")
    return {
        "refund_request_id": refund_request_id,
        "agent_id": request.agent_id,
        "response_type": request.response_type,
        "new_status": refund_request.status.value,
        "refund_amount": request.refund_amount,
        "timestamp": response.timestamp.isoformat()
    }


async def update_support_case_with_refund_request(case_number: str, refund_case_id: str):
    """Update support case with the newly created refund request ID"""
    try:
        import httpx
        support_service_url = "http://support-service:8001"
        
        # Update support case type and link refund request
        update_data = {
            "case_type": "refund",
            "refund_request_id": refund_case_id  # Send refund_case_id as refund_request_id for backward compatibility
        }
        
        # Send to support service
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{support_service_url}/support-cases/{case_number}/update-type",
                json=update_data,
                timeout=30.0
            )
            response.raise_for_status()
            print(f"✅ Successfully updated support case {case_number} with refund request {refund_case_id}")
    except Exception as e:
        print(f"⚠️ Failed to update support case {case_number}: {e}")
        # Don't fail refund creation if support service update fails

async def notify_support_service(refund_request, response):
    """Notify support service about refund decision to update timeline"""
    try:
        import httpx
        support_service_url = "http://support-service:8001"
        
        # Prepare refund feedback data
        feedback_data = {
            "author_id": "refund_service",
            "author_type": "refund_service", 
            "content": f"Refund {response.response_type.value}: {response.response_content}",
            "comment_type": "refund_feedback",
            "is_internal": False
        }
        
        # Add refund amount info if approved
        if response.refund_amount:
            feedback_data["content"] += f" - Approved amount: {response.refund_amount.format()}"
        
        # Send to support service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{support_service_url}/support-cases/{refund_request.support_case_number}/comments",
                json=feedback_data,
                timeout=30.0
            )
            response.raise_for_status()
            print(f"✅ Successfully notified support service about refund decision")
    except Exception as e:
        print(f"⚠️ Failed to notify support service: {e}")
        # Don't fail the refund decision if support service notification fails


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
    refund_case = dependencies.refund_request_repository.find_by_id(refund_case_id)
    
    if not refund_case:
        raise HTTPException(status_code=404, detail="Refund case not found")
    
    case_number = getattr(refund_case, 'support_case_number', None)
    if not case_number:
        case_number = getattr(refund_case, 'case_number', None)
    
    # Use refund_request_id as refund_case_id to match frontend expectations
    refund_case_id_val = getattr(refund_case, 'refund_request_id', None)
    if not refund_case_id_val:
        refund_case_id_val = getattr(refund_case, 'refund_case_id', f"RC-{refund_case_id}")
    
    return {
        "refund_case_id": refund_case_id_val if refund_case_id_val else f"RC-{refund_case_id}",
        "case_number": case_number if case_number else "SC-unknown",
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
    refund_case = dependencies.refund_request_repository.find_by_id(refund_case_id)
    
    if not refund_case:
        # Instead of hardcoded mock data, return 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Refund case {refund_case_id} not found"
        )
    
    # TODO: Implement proper detailed case retrieval with refund request and support case details
    case_number = getattr(refund_case, 'support_case_number', None)
    if not case_number:
        case_number = getattr(refund_case, 'case_number', None)
    
    # Use refund_request_id as refund_case_id to match frontend expectations
    refund_case_id_val = getattr(refund_case, 'refund_request_id', None)
    if not refund_case_id_val:
        refund_case_id_val = getattr(refund_case, 'refund_case_id', f"RC-{refund_case_id}")
    
    # Handle status enum conversion
    status_obj = getattr(refund_case, 'status', None)
    status_str = "pending"
    if status_obj:
        if hasattr(status_obj, 'value'):
            status_str = status_obj.value
        else:
            status_str = str(status_obj)
    
    # For now, return basic structure with default/fallback values
    return {
        "refund_case_id": refund_case_id_val if refund_case_id_val else f"RC-{refund_case_id}",
        "case_number": case_number if case_number else "SC-unknown",
        "customer_id": getattr(refund_case, 'customer_id', "unknown-customer"),
        "order_id": getattr(refund_case, 'order_id', "ORD-unknown"),
        "status": status_str,
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