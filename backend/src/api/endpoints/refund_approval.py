"""Refund approval API endpoints for support agents."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.infrastructure.auth.auth_middleware import get_current_support_agent
from src.domain.entities.refund_case import RefundCase
from src.domain.entities.support_agent import SupportAgent
from src.application.services.refund_approval_service import RefundApprovalService
from src.domain.repositories.refund_case_repository import RefundCaseRepository

router = APIRouter(prefix="/api/v1", tags=["refund-approval"])


@router.post(
    "/refund-cases/{refund_id}/approve",
    response_model=RefundCase,
    status_code=status.HTTP_200_OK,
)
async def approve_refund(
    refund_id: UUID,
    approved_amount: Optional[float] = None,
    current_agent: SupportAgent = Depends(get_current_support_agent),
    refund_case_repo: RefundCaseRepository = Depends(),
    approval_service: RefundApprovalService = Depends(),
):
    """Approve a refund case."""
    # Get the refund case
    refund_case = refund_case_repo.get_by_id(refund_id)
    if not refund_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Refund case not found"
        )

    try:
        # Approve the refund case
        updated_case = approval_service.approve_refund(
            refund_case=refund_case,
            agent=current_agent,
            current_date=datetime.now(),
            approved_amount=approved_amount,
        )

        # Save the approved case
        return refund_case_repo.save(updated_case)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/refund-cases/{refund_id}/cancel",
    response_model=RefundCase,
    status_code=status.HTTP_200_OK,
)
async def cancel_refund(
    refund_id: UUID,
    current_agent: SupportAgent = Depends(get_current_support_agent),
    refund_case_repo: RefundCaseRepository = Depends(),
    approval_service: RefundApprovalService = Depends(),
):
    """Cancel a refund case."""
    # Get the refund case
    refund_case = refund_case_repo.get_by_id(refund_id)
    if not refund_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Refund case not found"
        )

    try:
        # Cancel the refund case
        updated_case = approval_service.cancel_refund(
            refund_case=refund_case, agent=current_agent, current_date=datetime.now()
        )

        # Save the cancelled case
        return refund_case_repo.save(updated_case)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/refund-cases/pending",
    response_model=list[RefundCase],
    status_code=status.HTTP_200_OK,
)
async def get_pending_refunds(
    current_agent: SupportAgent = Depends(get_current_support_agent),
    refund_case_repo: RefundCaseRepository = Depends(),
):
    """Get all pending refund cases for approval."""
    return refund_case_repo.find_by_status("pending")
