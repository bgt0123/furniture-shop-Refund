from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from models.support_case import SupportCase, SupportCaseStatus
from services.support_case_service import SupportCaseService
from schemas.support_case import SupportCaseCreate, SupportCaseResponse
from database.session import get_db


router = APIRouter(prefix="/support/cases", tags=["support_cases"])


@router.post("/", response_model=SupportCaseResponse)
async def create_support_case(
    support_case_data: SupportCaseCreate, db: Session = Depends(get_db)
):
    """Create a new support case."""
    try:
        service = SupportCaseService(db)
        support_case = service.create_support_case(
            customer_id=support_case_data.customer_id,
            order_id=support_case_data.order_id,
            products=support_case_data.products,
            issue_description=support_case_data.issue_description,
            attachments=support_case_data.attachments or [],
            intends_refund=support_case_data.intends_refund,
        )
        return SupportCaseResponse.from_orm(support_case)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{case_id}", response_model=SupportCaseResponse)
async def get_support_case(case_id: UUID, db: Session = Depends(get_db)):
    """Get support case by ID."""
    service = SupportCaseService(db)
    support_case = service.get_support_case(case_id)
    if not support_case:
        raise HTTPException(status_code=404, detail="Support case not found")
    return SupportCaseResponse.from_orm(support_case)


@router.get("/customer/{customer_id}", response_model=List[SupportCaseResponse])
async def get_customer_support_cases(customer_id: UUID, db: Session = Depends(get_db)):
    """Get all support cases for a customer."""
    service = SupportCaseService(db)
    support_cases = service.get_customer_support_cases(customer_id)
    return [SupportCaseResponse.from_orm(case) for case in support_cases]


@router.patch("/{case_id}/close", response_model=SupportCaseResponse)
async def close_support_case(case_id: UUID, db: Session = Depends(get_db)):
    """Close a support case."""
    service = SupportCaseService(db)
    support_case = service.close_support_case(case_id)
    if not support_case:
        raise HTTPException(status_code=400, detail="Cannot close support case")
    return SupportCaseResponse.from_orm(support_case)
