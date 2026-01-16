"""Refund cases endpoints."""

from fastapi import APIRouter, Depends
from typing import List

from src.infrastructure.auth.auth_middleware import get_current_user

router = APIRouter(prefix="/refund-cases", tags=["Refund Cases"])


@router.get("/", response_model=List)
async def get_refund_cases(current_user=Depends(get_current_user)):
    """Get user's refund cases."""
    # TODO: Implement actual refund cases retrieval
    return []


@router.post("/")
async def create_refund_case(current_user=Depends(get_current_user)):
    """Create a new refund case."""
    # TODO: Implement refund case creation
    return {"message": "Refund case created"}


@router.get("/{refund_id}")
async def get_refund_case(refund_id: str, current_user=Depends(get_current_user)):
    """Get specific refund case."""
    # TODO: Implement refund case retrieval
    return {"id": refund_id, "status": "pending"}


@router.put("/{refund_id}/approve")
async def approve_refund(refund_id: str, current_user=Depends(get_current_user)):
    """Approve refund case."""
    # TODO: Implement refund approval
    return {"id": refund_id, "status": "approved"}
