"""Support cases endpoints."""

from fastapi import APIRouter, Depends
from typing import List

from src.infrastructure.auth.auth_middleware import get_current_user

router = APIRouter(prefix="/support-cases", tags=["Support Cases"])


@router.get("/", response_model=List)
async def get_support_cases(current_user=Depends(get_current_user)):
    """Get user's support cases."""
    # TODO: Implement actual support cases retrieval
    return []


@router.post("/")
async def create_support_case(current_user=Depends(get_current_user)):
    """Create a new support case."""
    # TODO: Implement support case creation
    return {"message": "Support case created"}


@router.get("/{case_id}")
async def get_support_case(case_id: str, current_user=Depends(get_current_user)):
    """Get specific support case."""
    # TODO: Implement support case retrieval
    return {"id": case_id, "status": "open"}


@router.put("/{case_id}")
async def update_support_case(case_id: str, current_user=Depends(get_current_user)):
    """Update support case."""
    # TODO: Implement support case update
    return {"id": case_id, "status": "updated"}
