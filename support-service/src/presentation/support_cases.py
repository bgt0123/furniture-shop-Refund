"""API routes for Support Cases"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
from uuid import uuid4

from presentation.dependencies import get_dependencies

router = APIRouter(prefix="/support-cases", tags=["support-cases"])


# Import CaseType from domain
from domain.support_case import CaseType

# Pydantic models for request/response
class CreateSupportCaseRequest(BaseModel):
    customer_id: str
    case_type: str  # "question" or "refund"
    subject: str
    description: str
    refund_request_id: Optional[str] = None
    evidence_files: Optional[List[str]] = None  # File paths/URLs
    order_id: Optional[str] = None
    product_ids: Optional[List[str]] = None
    delivery_date: Optional[str] = None  # ISO format date string


class SupportCaseResponse(BaseModel):
    case_number: str
    customer_id: str
    case_type: str
    subject: str
    description: str
    status: str
    refund_request_id: Optional[str] = None
    assigned_agent_id: Optional[str] = None
    order_id: Optional[str] = None
    product_ids: Optional[List[str]] = None
    delivery_date: Optional[str] = None
    comments: Optional[List[dict]] = None
    created_at: str
    updated_at: str


class CommentResponse(BaseModel):
    comment_id: str
    case_number: str
    author_id: str
    author_type: str
    content: str
    comment_type: str
    attachments: Optional[List[str]] = None
    timestamp: str
    is_internal: bool


class SupportResponseRequest(BaseModel):
    sender_id: str
    sender_type: str  # "customer" or "agent"
    content: str
    message_type: str  # "question", "answer", "status_update", "close_case"
    attachments: Optional[List[str]] = None
    is_internal: bool = False


class AddCommentRequest(BaseModel):
    author_id: str
    author_type: str  # "customer", "agent", "refund_service"
    content: str
    comment_type: str  # "customer_comment", "agent_response", "refund_feedback"
    attachments: Optional[List[str]] = None
    is_internal: bool = False


@router.post("/", response_model=SupportCaseResponse)
async def create_support_case(request: CreateSupportCaseRequest):
    """Create a new support case"""
    dependencies = get_dependencies()
    
    try:
        result = dependencies.create_support_case.execute(
            customer_id=request.customer_id,
            case_type=request.case_type,
            subject=request.subject,
            description=request.description,
            refund_request_id=request.refund_request_id,
            order_id=request.order_id,
            product_ids=request.product_ids,
            delivery_date=request.delivery_date
        )
        
        support_case = result["support_case"]
        
        return SupportCaseResponse(
            case_number=result["case_number"],
            customer_id=support_case.customer_id,
            case_type=support_case.case_type.value,
            subject=support_case.subject,
            description=support_case.description,
            status=support_case.status.value,
            refund_request_id=support_case.refund_request_id,
            assigned_agent_id=support_case.assigned_agent_id,
            order_id=support_case.order_id,
            product_ids=support_case.product_ids,
            delivery_date=support_case.delivery_date.isoformat() if support_case.delivery_date else None,
            created_at=support_case.created_at.isoformat(),
            updated_at=support_case.updated_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{case_number}", response_model=SupportCaseResponse)
async def get_support_case(case_number: str):
    """Get a support case by ID"""
    try:
        dependencies = get_dependencies()
        
        # Find support case
        support_case = dependencies.support_case_repository.find_by_case_number(case_number)
        
        print(f"DEBUG: Support case found: {support_case is not None}")
        if support_case:
            print(f"DEBUG: Case number: {support_case.case_number}")
            print(f"DEBUG: Comments attribute exists: {hasattr(support_case, 'comments')}")
            if hasattr(support_case, 'comments'):
                print(f"DEBUG: Comments list: {support_case.comments}")
        
        if not support_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Support case {case_number} not found"
            )
        
        # Format comments for response
        comments_list = support_case.comments if support_case.comments is not None else []
        print(f"DEBUG: Processing {len(comments_list)} comments")
        formatted_comments = []
        for i, comment in enumerate(comments_list):
            print(f"DEBUG: Comment {i}: {comment}")
            formatted_comments.append({
                "comment_id": comment.comment_id,
                "author_id": comment.author_id,
                "author_type": comment.author_type,
                "content": comment.content,
                "comment_type": comment.comment_type.value,
                "timestamp": comment.timestamp.isoformat(),
                "attachments": comment.attachments,
                "is_internal": comment.is_internal
            })
        
        return SupportCaseResponse(
            case_number=support_case.case_number,
            customer_id=support_case.customer_id,
            case_type=support_case.case_type.value,
            subject=support_case.subject,
            description=support_case.description,
            status=support_case.status.value,
            refund_request_id=support_case.refund_request_id,
            assigned_agent_id=support_case.assigned_agent_id,
            order_id=support_case.order_id,
            product_ids=support_case.product_ids,
            delivery_date=support_case.delivery_date.isoformat() if support_case.delivery_date else None,
            comments=formatted_comments,
            created_at=support_case.created_at.isoformat(),
            updated_at=support_case.updated_at.isoformat()
        )
    except Exception as e:
        print(f"ERROR in get_support_case: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/customer/{customer_id}", response_model=List[SupportCaseResponse])
async def get_customer_support_cases(customer_id: str):
    """Get all support cases for a customer"""
    dependencies = get_dependencies()
    
    # Find customer's support cases
    support_cases = dependencies.support_case_repository.find_by_customer_id(customer_id)
    
    return [
        SupportCaseResponse(
            case_number=case.case_number,
            customer_id=case.customer_id,
            case_type=case.case_type.value,
            subject=case.subject,
            description=case.description,
            status=case.status.value,
            refund_request_id=case.refund_request_id,
            assigned_agent_id=case.assigned_agent_id,
            created_at=case.created_at.isoformat(),
            updated_at=case.updated_at.isoformat()
        )
         for case in support_cases
 ]


@router.get("/", response_model=List[SupportCaseResponse])
async def get_all_support_cases():
    """Get all support cases (for agents)"""
    dependencies = get_dependencies()
    
    # Find all support cases
    support_cases = dependencies.support_case_repository.find_all()
    
    return [
        SupportCaseResponse(
            case_number=case.case_number,
            customer_id=case.customer_id,
            case_type=case.case_type.value,
            subject=case.subject,
            description=case.description,
            status=case.status.value,
            refund_request_id=case.refund_request_id,
            assigned_agent_id=case.assigned_agent_id,
            created_at=case.created_at.isoformat(),
            updated_at=case.updated_at.isoformat()
        )
        for case in support_cases
    ]


@router.post("/{case_number}/responses")
async def add_response(case_number: str, request: SupportResponseRequest):
    """Add a response to a support case"""
    dependencies = get_dependencies()
    
    try:
        result = dependencies.add_response.execute(
            case_number=case_number,
            sender_id=request.sender_id,
            sender_type=request.sender_type,
            content=request.content,
            message_type=request.message_type,
            attachments=request.attachments,
            is_internal=request.is_internal
        )
        
        response = result["response"]
        
        return {
            "response_id": response.response_id,
            "case_number": response.case_number,
            "sender_id": response.sender_id,
            "sender_type": response.sender_type.value,
            "content": response.content,
            "message_type": response.message_type.value,
            "timestamp": response.timestamp.isoformat(),
            "attachments": response.attachments,
            "is_internal": response.is_internal
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{case_number}/assign/{agent_id}")
async def assign_agent(case_number: str, agent_id: str):
    """Assign an agent to a support case"""
    dependencies = get_dependencies()
    
    try:
        result = dependencies.assign_agent.execute(
            case_number=case_number,
            agent_id=agent_id
        )
        
        support_case = result["support_case"]
        
        return {
            "case_number": support_case.case_number,
            "assigned_agent_id": support_case.assigned_agent_id,
            "status": support_case.status.value,
            "updated_at": support_case.updated_at.isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


class UpdateSupportCaseRequest(BaseModel):
    subject: str
    description: str
    case_type: str
    user_role: str  # "customer" or "agent"
    user_id: str

class UpdateCaseTypeRequest(BaseModel):
    case_type: str
    refund_request_id: Optional[str] = None


@router.put("/{case_number}/close")
async def close_case(case_number: str):
    """Close a support case"""
    dependencies = get_dependencies()
    
    try:
        result = dependencies.close_case.execute(case_number=case_number)
        
        support_case = result["support_case"]
        
        return {
            "case_number": support_case.case_number,
            "status": support_case.status.value,
            "updated_at": support_case.updated_at.isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{case_number}/reopen")
async def reopen_case(case_number: str):
    """Reopen a support case"""
    dependencies = get_dependencies()
    
    try:
        result = dependencies.reopen_case.execute(case_number=case_number)
        
        support_case = result["support_case"]
        
        return {
            "case_number": support_case.case_number,
            "status": support_case.status.value,
            "updated_at": support_case.updated_at.isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{case_number}/update-type")
async def update_case_type(case_number: str, request: UpdateCaseTypeRequest):
    """Update case type and optionally link refund request"""
    dependencies = get_dependencies()
    
    try:
        result = dependencies.update_case_type.execute(
            case_number=case_number,
            case_type=request.case_type,
            refund_request_id=request.refund_request_id
        )
        
        support_case = result["support_case"]
        
        return SupportCaseResponse(
            case_number=support_case.case_number,
            customer_id=support_case.customer_id,
            case_type=support_case.case_type.value,
            subject=support_case.subject,
            description=support_case.description,
            status=support_case.status.value,
            refund_request_id=support_case.refund_request_id,
            assigned_agent_id=support_case.assigned_agent_id,
            created_at=support_case.created_at.isoformat(),
            updated_at=support_case.updated_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{case_number}")
async def update_support_case(case_number: str, request: UpdateSupportCaseRequest):
    """Update a support case (role-based access control)"""
    dependencies = get_dependencies()
    
    # Role-based access control: Only customers can update their own cases
    if request.user_role == "agent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agents cannot edit support cases. Customers must submit updates through the support channels."
        )
    
    try:
        # Create a new use case for updating support cases
        # For now, we'll implement a simplified version
        support_case = dependencies.support_case_repository.find_by_case_number(case_number)
        
        if not support_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Support case {case_number} not found"
            )
        
        # Verify customer owns the case
        if support_case.customer_id != request.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own support cases"
            )
        
        # Update case fields
        support_case.subject = request.subject
        support_case.description = request.description
        # Convert string to CaseType enum
        if request.case_type == "refund":
            support_case.case_type = CaseType.REFUND
        else:
            support_case.case_type = CaseType.QUESTION
        
        # Save updated case
        dependencies.support_case_repository.save(support_case)
        
        return SupportCaseResponse(
            case_number=support_case.case_number,
            customer_id=support_case.customer_id,
            case_type=support_case.case_type.value,
            subject=support_case.subject,
            description=support_case.description,
            status=support_case.status.value,
            refund_request_id=support_case.refund_request_id,
            assigned_agent_id=support_case.assigned_agent_id,
            created_at=support_case.created_at.isoformat(),
            updated_at=support_case.updated_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{case_number}/upload-evidence")
async def upload_evidence(
    case_number: str,
    files: List[UploadFile] = File(...)
):
    """Upload evidence photos for a support case"""
    dependencies = get_dependencies()
    
    # Validate that the case exists and is not closed
    support_case = dependencies.support_case_repository.find_by_case_number(case_number)
    
    if not support_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Support case {case_number} not found"
        )
    
    if support_case.is_closed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot upload evidence to closed support case {case_number}"
        )
    
    # TODO: Integrate with file storage service
    file_names = [file.filename for file in files if file.filename]
    
    return {
        "case_number": case_number,
        "uploaded_files": file_names,
        "message": f"Successfully uploaded {len(file_names)} files"
    }


@router.get("/{case_number}/evidence")
async def get_evidence(case_number: str):
    """Get list of evidence files for a support case"""
    # TODO: Integrate with file storage service
    return {
        "case_number": case_number,
        "evidence_files": ["photo1.jpg", "photo2.png"],
        "message": "Mock evidence files"
    }


@router.post("/{case_number}/comments", response_model=CommentResponse)
async def add_comment(case_number: str, request: AddCommentRequest):
    """Add a comment to a support case"""
    dependencies = get_dependencies()
    
    try:
        result = dependencies.add_comment.execute(
            case_number=case_number,
            author_id=request.author_id,
            author_type=request.author_type,
            content=request.content,
            comment_type=request.comment_type,
            attachments=request.attachments if request.attachments is not None else [],
            is_internal=request.is_internal
        )
        
        comment = result["comment"]
        
        return CommentResponse(
            comment_id=comment.comment_id,
            case_number=comment.case_number,
            author_id=comment.author_id,
            author_type=comment.author_type,
            content=comment.content,
            comment_type=comment.comment_type.value,
            attachments=comment.attachments,
            timestamp=comment.timestamp.isoformat(),
            is_internal=comment.is_internal
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )# Trigger reload
