from fastapi import APIRouter, HTTPException, Depends, Request, Query, Body
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from models.refund_case import RefundCase, RefundCaseStatus
from services.refund_case_service import RefundCaseService
from services.agent_service import AgentService
from schemas.refund_case import RefundCaseResponse
from schemas.refund_case_admin import RefundCaseRejection
from database.session import get_db

router = APIRouter(prefix="/admin/refunds/cases", tags=["admin_refunds"])


def get_agent_id(request) -> UUID:
    """Dependency to extract agent ID from request headers."""
    # Extract from X-Agent-ID header
    agent_id_header = request.headers.get("X-Agent-ID")
    if agent_id_header:
        try:
            return UUID(agent_id_header)
        except ValueError:
            pass

    # Fallback to mock ID for testing
    return UUID("00000000-0000-0000-0000-000000000000")


def verify_agent_permissions(request: Request, db: Session = Depends(get_db)) -> UUID:
    """Verify agent has permission to perform admin actions."""
    agent_id = get_agent_id(request)
    agent_service = AgentService(db)
    agent = agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_id


@router.get("/pending")
async def get_pending_refund_cases(
    request: Request,
    agent_id: UUID = Depends(verify_agent_permissions),
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Get pending refund cases for agent dashboard."""
    try:
        refund_service = RefundCaseService(db)
        # Get pending refund cases
        refund_cases = refund_service.get_refund_cases_by_status(
            "Pending", limit, offset
        )

        print(f"Found {len(refund_cases)} pending refund cases")
        return [RefundCaseResponse.from_orm(case) for case in refund_cases]
    except Exception as e:
        print(f"Error in /pending endpoint: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/test")
async def test_admin_endpoint():
    """Test endpoint without authentication."""
    return {"message": "Admin endpoint works!"}


@router.get("/", response_model=List[RefundCaseResponse])
async def get_admin_refund_cases(
    request: Request,
    status: Optional[str] = None,
    customer_id: Optional[UUID] = None,
    agent_id: UUID = Depends(verify_agent_permissions),
    db: Session = Depends(get_db),
):
    """Get all refund cases for admin with filtering."""
    try:
        refund_service = RefundCaseService(db)

        if customer_id:
            refund_cases = refund_service.get_customer_refund_cases(customer_id)
        elif status:
            refund_cases = refund_service.get_refund_cases_by_status(status)
        else:
            refund_cases = refund_service.get_all_refund_cases()

        return [RefundCaseResponse.from_orm(case) for case in refund_cases]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{refund_id}", response_model=RefundCaseResponse)
async def get_admin_refund_case(
    request: Request,
    refund_id: UUID,
    agent_id: UUID = Depends(verify_agent_permissions),
    db: Session = Depends(get_db),
):
    """Get refund case details for admin review."""
    refund_service = RefundCaseService(db)
    refund_case = refund_service.get_refund_case(refund_id)
    if not refund_case:
        raise HTTPException(status_code=404, detail="Refund case not found")

    return RefundCaseResponse.from_orm(refund_case)


@router.post("/{refund_id}/approve", response_model=RefundCaseResponse)
async def admin_approve_refund_case(
    request: Request,
    refund_id: UUID,
    agent_id: UUID = Depends(verify_agent_permissions),
    db: Session = Depends(get_db),
):
    """Approve a refund case."""
    try:
        agent_service = AgentService(db)
        refund_service = RefundCaseService(db)

        agent = agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        refund_case = refund_service.approve_refund_case(refund_id, agent_id)
        if not refund_case:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve refund case {refund_id}: case not found or not in PENDING status",
            )

        return RefundCaseResponse.from_orm(refund_case)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{refund_id}/reject", response_model=RefundCaseResponse)
async def admin_reject_refund_case(
    request: Request,
    refund_id: UUID,
    rejection_data: RefundCaseRejection,
    agent_id: UUID = Depends(verify_agent_permissions),
    db: Session = Depends(get_db),
):
    """Reject a refund case (using request body)."""
    try:
        agent_service = AgentService(db)
        refund_service = RefundCaseService(db)

        agent = agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        refund_case = refund_service.reject_refund_case(
            refund_id, agent_id, rejection_data.reason
        )
        if not refund_case:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject refund case {refund_id}: case not found or not in PENDING status",
            )

        return RefundCaseResponse.from_orm(refund_case)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{refund_id}/reject/query", response_model=RefundCaseResponse)
async def admin_reject_refund_case_query(
    request: Request,
    refund_id: UUID,
    reason: str = Query(..., description="Reason for rejecting the refund"),
    agent_id: UUID = Depends(verify_agent_permissions),
    db: Session = Depends(get_db),
):
    """Reject a refund case (using query parameter)."""
    try:
        agent_service = AgentService(db)
        refund_service = RefundCaseService(db)

        agent = agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        refund_case = refund_service.reject_refund_case(refund_id, agent_id, reason)
        if not refund_case:
            raise HTTPException(status_code=400, detail="Cannot reject refund case")

        return RefundCaseResponse.from_orm(refund_case)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
