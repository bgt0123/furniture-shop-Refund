from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from models.refund_case import RefundCase, RefundCaseStatus
from services.refund_case_service import RefundCaseService
from services.support_case_service import SupportCaseService
from schemas.refund_case import RefundCaseCreate, RefundCaseResponse
from database.session import get_db


router = APIRouter(prefix="/refunds/cases", tags=["refund_cases"])
support_router = APIRouter(prefix="/support/cases", tags=["support_cases"])


# Endpoint for creating refund case from support case
@support_router.post("/{case_id}/refunds", response_model=RefundCaseResponse)
async def create_refund_case(
    case_id: UUID, refund_case_data: RefundCaseCreate, db: Session = Depends(get_db)
):
    """Create a refund case for a support case."""
    try:
        support_service = SupportCaseService(db)
        refund_service = RefundCaseService(db)

        # Verify support case exists
        support_case = support_service.get_support_case(case_id)
        if not support_case:
            raise HTTPException(status_code=404, detail="Support case not found")

        # Check that the customer owns this support case
        if str(refund_case_data.customer_id) != support_case.customer_id:
            raise HTTPException(
                status_code=403, detail="Customer does not own this support case"
            )

        # Check that the order matches
        if refund_case_data.order_id != support_case.order_id:
            raise HTTPException(
                status_code=400, detail="Order ID does not match support case"
            )

        # Create refund case
        refund_case = refund_service.create_refund_case(
            support_case_id=case_id,
            customer_id=refund_case_data.customer_id,
            order_id=refund_case_data.order_id,
            products=refund_case_data.products,
            reason=refund_case_data.reason,
            support_case=support_case,
        )

        return RefundCaseResponse.from_orm(refund_case)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[RefundCaseResponse])
async def get_refund_cases(
    status: str | None = None,
    customer_id: UUID | None = None,
    db: Session = Depends(get_db),
):
    """Get all refund cases with optional filtering."""
    refund_service = RefundCaseService(db)

    if customer_id:
        # Get by customer
        refund_cases = refund_service.get_customer_refund_cases(customer_id)
    elif status:
        # Get by status
        refund_cases = refund_service.get_refund_cases_by_status(status)
    else:
        # Get all refund cases
        refund_cases = refund_service.get_all_refund_cases()

    return [RefundCaseResponse.from_orm(case) for case in refund_cases]


@router.get("/customer/{customer_id}", response_model=List[RefundCaseResponse])
async def get_customer_refund_cases(customer_id: UUID, db: Session = Depends(get_db)):
    """Get all refund cases for a customer."""
    refund_service = RefundCaseService(db)
    refund_cases = refund_service.get_customer_refund_cases(customer_id)
    return [RefundCaseResponse.from_orm(case) for case in refund_cases]


@router.get("/{refund_id}", response_model=RefundCaseResponse)
async def get_refund_case(refund_id: UUID, db: Session = Depends(get_db)):
    """Get refund case by ID."""
    refund_service = RefundCaseService(db)
    refund_case = refund_service.get_refund_case(refund_id)
    if not refund_case:
        raise HTTPException(status_code=404, detail="Refund case not found")
    return RefundCaseResponse.from_orm(refund_case)


@router.post("/{refund_id}/approve", response_model=RefundCaseResponse)
async def approve_refund_case(refund_id: UUID, db: Session = Depends(get_db)):
    """Approve a refund case."""
    # In a real application, you'd get agent_id from authentication
    agent_id = UUID("00000000-0000-0000-0000-000000000000")  # Mock agent ID

    refund_service = RefundCaseService(db)
    refund_case = refund_service.approve_refund_case(refund_id, agent_id)
    if not refund_case:
        raise HTTPException(status_code=400, detail="Cannot approve refund case")
    return RefundCaseResponse.from_orm(refund_case)


@router.post("/{refund_id}/reject", response_model=RefundCaseResponse)
async def reject_refund_case(
    refund_id: UUID, reason: str, db: Session = Depends(get_db)
):
    """Reject a refund case."""
    # In a real application, you'd get agent_id from authentication
    agent_id = UUID("00000000-0000-0000-0000-000000000000")  # Mock agent ID

    refund_service = RefundCaseService(db)
    refund_case = refund_service.reject_refund_case(refund_id, agent_id, reason)
    if not refund_case:
        raise HTTPException(status_code=400, detail="Cannot reject refund case")
    return RefundCaseResponse.from_orm(refund_case)


@router.post("/{refund_id}/complete", response_model=RefundCaseResponse)
async def complete_refund_case(refund_id: UUID, db: Session = Depends(get_db)):
    """Mark refund case as completed."""
    refund_service = RefundCaseService(db)
    refund_case = refund_service.complete_refund_case(refund_id)
    if not refund_case:
        raise HTTPException(status_code=400, detail="Cannot complete refund case")
    return RefundCaseResponse.from_orm(refund_case)
