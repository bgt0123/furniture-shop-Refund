from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from src.middleware.auth import admin_only, agent_only
from src.services.refund_service import refund_case_service
from src.models.refund_case import RefundCase
from src.middleware.exceptions import AppException
from pydantic import BaseModel
import logging

router = APIRouter()

logger = logging.getLogger(__name__)


# Request/Response Models
class RefundRejectionRequest(BaseModel):
    reason: str


class RefundCaseAdminResponse(BaseModel):
    id: str
    support_case_id: str
    customer_id: str
    order_id: str
    status: str
    eligibility_status: str
    total_refund_amount: float
    created_at: str
    processed_at: Optional[str]
    rejection_reason: Optional[str]
    agent_id: Optional[str]


@router.get("/refunds/cases", response_model=List[RefundCaseAdminResponse])
async def get_all_refund_cases(
    status: Optional[str] = Query(None, description="Filter by status"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    user: dict = Depends(admin_only),
):
    """Get all refund cases for admin view"""
    try:
        cases = refund_case_service.get_all_refund_cases_admin(status, customer_id)

        # Convert to response format
        response_cases = []
        for case in cases:
            response_cases.append(
                RefundCaseAdminResponse(
                    id=case.id,
                    support_case_id=case.support_case_id,
                    customer_id=case.customer_id,
                    order_id=case.order_id,
                    status=case.status,
                    eligibility_status=case.eligibility_status,
                    total_refund_amount=case.total_refund_amount,
                    created_at=case.created_at.isoformat(),
                    processed_at=case.processed_at.isoformat()
                    if case.processed_at
                    else None,
                    rejection_reason=case.rejection_reason,
                    agent_id=case.agent_id,
                )
            )

        return response_cases
    except AppException as e:
        logger.error(f"Admin endpoint error: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Admin endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting refund cases: {str(e)}",
        )


@router.get("/refunds/cases/{refundId}", response_model=RefundCaseAdminResponse)
async def get_refund_case_admin(
    refundId: str,
    user: dict = Depends(agent_only),
):
    """Get refund case details for admin"""
    try:
        case = refund_case_service.get_refund_case_admin(refundId)

        return RefundCaseAdminResponse(
            id=case.id,
            support_case_id=case.support_case_id,
            customer_id=case.customer_id,
            order_id=case.order_id,
            status=case.status,
            eligibility_status=case.eligibility_status,
            total_refund_amount=case.total_refund_amount,
            created_at=case.created_at.isoformat(),
            processed_at=case.processed_at.isoformat() if case.processed_at else None,
            rejection_reason=case.rejection_reason,
            agent_id=case.agent_id,
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting refund case: {str(e)}",
        )


@router.post(
    "/refunds/cases/{refundId}/approve", response_model=RefundCaseAdminResponse
)
async def approve_refund_case(
    refundId: str,
    user: dict = Depends(agent_only),
):
    """Approve a refund case"""
    try:
        # Get agent ID from token
        agent_id = user.get("sub") or user.get("user_id")
        if not agent_id:
            raise HTTPException(
                status_code=400,
                detail="Agent ID not found in token",
            )

        case = refund_case_service.approve_refund_case(refundId, agent_id)

        return RefundCaseAdminResponse(
            id=case.id,
            support_case_id=case.support_case_id,
            customer_id=case.customer_id,
            order_id=case.order_id,
            status=case.status,
            eligibility_status=case.eligibility_status,
            total_refund_amount=case.total_refund_amount,
            created_at=case.created_at.isoformat(),
            processed_at=case.processed_at.isoformat() if case.processed_at else None,
            rejection_reason=case.rejection_reason,
            agent_id=case.agent_id,
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error approving refund case: {str(e)}",
        )


@router.post("/refunds/cases/{refundId}/reject", response_model=RefundCaseAdminResponse)
async def reject_refund_case(
    refundId: str,
    rejection_data: RefundRejectionRequest,
    user: dict = Depends(agent_only),
):
    """Reject a refund case"""
    try:
        # Get agent ID from token
        agent_id = user.get("sub") or user.get("user_id")
        if not agent_id:
            raise HTTPException(
                status_code=400,
                detail="Agent ID not found in token",
            )

        case = refund_case_service.reject_refund_case(
            refundId, agent_id, rejection_data.reason
        )

        return RefundCaseAdminResponse(
            id=case.id,
            support_case_id=case.support_case_id,
            customer_id=case.customer_id,
            order_id=case.order_id,
            status=case.status,
            eligibility_status=case.eligibility_status,
            total_refund_amount=case.total_refund_amount,
            created_at=case.created_at.isoformat(),
            processed_at=case.processed_at.isoformat() if case.processed_at else None,
            rejection_reason=case.rejection_reason,
            agent_id=case.agent_id,
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error rejecting refund case: {str(e)}",
        )
