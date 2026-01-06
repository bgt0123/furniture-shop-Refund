from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from src.middleware.auth import auth_required, customer_only
from src.services.support_service import support_case_service
from src.models.support_case import SupportCase
from src.middleware.exceptions import AppException
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


# Request/Response Models
class SupportCaseCreateRequest(BaseModel):
    order_id: str
    issue_description: str
    products: List[dict]
    attachments: Optional[List[dict]] = None


class SupportCaseResponse(BaseModel):
    id: str
    customer_id: str
    order_id: str
    issue_description: str
    status: str
    created_at: str
    closed_at: Optional[str] = None
    products: List[dict]
    attachments: List[dict]
    history: List[dict]

    @classmethod
    def from_entity(cls, entity: SupportCase):
        return cls(
            id=entity.id,
            customer_id=entity.customer_id,
            order_id=entity.order_id,
            issue_description=entity.issue_description,
            status=entity.status.value,
            created_at=entity.created_at.isoformat(),
            closed_at=entity.closed_at.isoformat() if entity.closed_at else None,
            products=entity.products or [],
            attachments=entity.attachments or [],
            history=entity.history or [],
        )


class SupportCaseUpdateRequest(BaseModel):
    issue_description: Optional[str] = None
    status: Optional[str] = None


class SupportCaseListResponse(BaseModel):
    cases: List[SupportCaseResponse]
    count: int


# Endpoints
@router.post(
    "/cases",
    summary="Create a new support case",
    description="Customers can create support cases for their orders",
    response_model=SupportCaseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_support_case(
    request: SupportCaseCreateRequest, token_data=Depends(customer_only)
):
    """Create a new support case"""
    try:
        # Extract user_id from token_data (which is a TokenData object)
        user_id = (
            token_data.user_id
            if hasattr(token_data, "user_id")
            else str(token_data.get("user_id"))
        )

        support_case = support_case_service.create_support_case(
            customer_id=user_id,
            order_id=request.order_id,
            issue_description=request.issue_description,
            products=request.products,
            attachments=request.attachments,
        )
        return SupportCaseResponse.from_entity(support_case)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/cases",
    summary="Get all support cases for current customer",
    description="Returns list of support cases for the authenticated customer",
    response_model=SupportCaseListResponse,
)
async def get_customer_support_cases(
    status: Optional[str] = Query(None, description="Filter by status (Open/Closed)"),
    skip: int = Query(0, description="Pagination offset"),
    limit: int = Query(100, description="Pagination limit"),
    token_data=Depends(customer_only),
):
    """Get all support cases for the authenticated customer"""
    try:
        # Extract user_id from token_data
        user_id = (
            token_data.user_id
            if hasattr(token_data, "user_id")
            else str(token_data.get("user_id"))
        )

        cases = support_case_service.get_customer_support_cases(user_id, status)

        # Apply pagination
        paginated_cases = cases[skip : skip + limit]

        return SupportCaseListResponse(
            cases=[SupportCaseResponse.from_entity(case) for case in paginated_cases],
            count=len(paginated_cases),
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/cases/{case_id}",
    summary="Get support case details",
    description="Get detailed information about a specific support case",
    response_model=SupportCaseResponse,
)
async def get_support_case(case_id: str, token_data=Depends(customer_only)):
    """Get support case details"""
    try:
        # Extract user_id from token_data
        user_id = (
            token_data.user_id
            if hasattr(token_data, "user_id")
            else str(token_data.get("user_id"))
        )

        support_case = support_case_service.get_support_case(case_id, user_id)
        return SupportCaseResponse.from_entity(support_case)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch(
    "/cases/{case_id}",
    summary="Update support case",
    description="Customers can update their support case details",
    response_model=SupportCaseResponse,
)
async def update_support_case(
    case_id: str, request: SupportCaseUpdateRequest, token_data=Depends(customer_only)
):
    """Update support case details"""
    try:
        # Extract user_id from token_data
        user_id = (
            token_data.user_id
            if hasattr(token_data, "user_id")
            else str(token_data.get("user_id"))
        )

        # Get the current case
        support_case = support_case_service.get_support_case(case_id, user_id)

        # Apply updates
        if request.issue_description:
            support_case.issue_description = request.issue_description

        # Save changes
        updated_case = support_case_service.repository.update(
            case_id, support_case.to_dict()
        )

        return SupportCaseResponse.from_entity(updated_case)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch(
    "/cases/{case_id}/close",
    summary="Close a support case",
    description="Customers can close their own support cases",
    response_model=SupportCaseResponse,
)
async def close_support_case(case_id: str, token_data=Depends(customer_only)):
    """Close a support case"""
    try:
        # Extract user_id from token_data
        user_id = (
            token_data.user_id
            if hasattr(token_data, "user_id")
            else str(token_data.get("user_id"))
        )

        closed_case = support_case_service.close_support_case(case_id, user_id)
        return SupportCaseResponse.from_entity(closed_case)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/cases/{case_id}/attachments",
    summary="Add attachment to support case",
    description="Add an attachment to an existing support case",
    response_model=SupportCaseResponse,
)
async def add_attachment(
    case_id: str, attachment: dict, token_data=Depends(customer_only)
):
    """Add attachment to support case"""
    try:
        # Extract user_id from token_data
        user_id = (
            token_data.user_id
            if hasattr(token_data, "user_id")
            else str(token_data.get("user_id"))
        )

        updated_case = support_case_service.add_attachment_to_case(
            case_id, user_id, attachment
        )
        return SupportCaseResponse.from_entity(updated_case)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/cases/{case_id}/refund-eligibility",
    summary="Check refund eligibility",
    description="Check if products in support case are eligible for refund",
    response_model=dict,
)
async def check_refund_eligibility(
    case_id: str,
    product_ids: List[str] = Query([], description="Product IDs to check"),
    token_data=Depends(customer_only),
):
    """Check refund eligibility for products in support case"""
    try:
        # Extract user_id from token_data
        user_id = (
            token_data.user_id
            if hasattr(token_data, "user_id")
            else str(token_data.get("user_id"))
        )

        eligibility = support_case_service.validate_refund_eligibility(
            case_id, user_id, product_ids
        )
        return eligibility
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/cases",
    summary="Get all support cases for current customer",
    description="Returns list of support cases for the authenticated customer",
    response_model=SupportCaseListResponse,
)
async def get_customer_support_cases(
    status: Optional[str] = Query(None, description="Filter by status (Open/Closed)"),
    skip: int = Query(0, description="Pagination offset"),
    limit: int = Query(100, description="Pagination limit"),
    token_data: dict = Depends(customer_only),
):
    """Get all support cases for the authenticated customer"""
    try:
        cases = support_case_service.get_customer_support_cases(
            token_data.user_id, status
        )

        # Apply pagination
        paginated_cases = cases[skip : skip + limit]

        return SupportCaseListResponse(
            cases=[SupportCaseResponse.from_entity(case) for case in paginated_cases],
            count=len(paginated_cases),
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/cases/{case_id}",
    summary="Get support case details",
    description="Get detailed information about a specific support case",
    response_model=SupportCaseResponse,
)
async def get_support_case(case_id: str, token_data: dict = Depends(customer_only)):
    """Get support case details"""
    try:
        support_case = support_case_service.get_support_case(
            case_id, token_data.user_id
        )
        return SupportCaseResponse.from_entity(support_case)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch(
    "/cases/{case_id}",
    summary="Update support case",
    description="Customers can update their support case details",
    response_model=SupportCaseResponse,
)
async def update_support_case(
    case_id: str,
    request: SupportCaseUpdateRequest,
    token_data: dict = Depends(customer_only),
):
    """Update support case details"""
    try:
        # Get the current case
        support_case = support_case_service.get_support_case(
            case_id, token_data.user_id
        )

        # Apply updates
        if request.issue_description:
            support_case.issue_description = request.issue_description

        # Save changes
        updated_case = support_case_service.repository.update(
            case_id, support_case.to_dict()
        )

        return SupportCaseResponse.from_entity(updated_case)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch(
    "/cases/{case_id}/close",
    summary="Close a support case",
    description="Customers can close their own support cases",
    response_model=SupportCaseResponse,
)
async def close_support_case(case_id: str, token_data: dict = Depends(customer_only)):
    """Close a support case"""
    try:
        closed_case = support_case_service.close_support_case(
            case_id, token_data.user_id
        )
        return SupportCaseResponse.from_entity(closed_case)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/cases/{case_id}/attachments",
    summary="Add attachment to support case",
    description="Add an attachment to an existing support case",
    response_model=SupportCaseResponse,
)
async def add_attachment(
    case_id: str, attachment: dict, token_data: dict = Depends(customer_only)
):
    """Add attachment to support case"""
    try:
        updated_case = support_case_service.add_attachment_to_case(
            case_id, token_data.user_id, attachment
        )
        return SupportCaseResponse.from_entity(updated_case)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/cases/{case_id}/refund-eligibility",
    summary="Check refund eligibility",
    description="Check if products in support case are eligible for refund",
    response_model=dict,
)
async def check_refund_eligibility(
    case_id: str,
    product_ids: List[str] = Query([], description="Product IDs to check"),
    token_data: dict = Depends(customer_only),
):
    """Check refund eligibility for products in support case"""
    try:
        eligibility = support_case_service.validate_refund_eligibility(
            case_id, token_data.user_id, product_ids
        )
        return eligibility
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
