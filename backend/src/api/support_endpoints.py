from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID
from models.support_case import SupportCase, SupportCaseStatus
from services.support_case_service import SupportCaseService
from schemas.support_case import SupportCaseCreate, SupportCaseResponse


router = APIRouter(prefix="/support/cases", tags=["support_cases"])


# Create service instance
service = SupportCaseService()


@router.post("/", response_model=SupportCaseResponse)
async def create_support_case(support_case_data: SupportCaseCreate):
    """Create a new support case."""
    try:
        support_case = service.create_support_case(
            customer_id=support_case_data.customer_id,
            order_id=support_case_data.order_id,
            products=support_case_data.products,
            issue_description=support_case_data.issue_description,
            attachments=support_case_data.attachments or [],
        )
        return SupportCaseResponse.from_orm(support_case)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{case_id}", response_model=SupportCaseResponse)
async def get_support_case(case_id: UUID):
    """Get support case by ID."""
    support_case = service.get_support_case(case_id)
    if not support_case:
        raise HTTPException(status_code=404, detail="Support case not found")
    return SupportCaseResponse.from_orm(support_case)


@router.get("/customer/{customer_id}", response_model=List[SupportCaseResponse])
async def get_customer_support_cases(customer_id: UUID):
    """Get all support cases for a customer."""
    support_cases = service.get_customer_support_cases(customer_id)
    return [SupportCaseResponse.from_orm(case) for case in support_cases]


@router.patch("/{case_id}/close", response_model=SupportCaseResponse)
async def close_support_case(case_id: UUID):
    """Close a support case."""
    support_case = service.close_support_case(case_id)
    if not support_case:
        raise HTTPException(status_code=400, detail="Cannot close support case")
    return SupportCaseResponse.from_orm(support_case)
