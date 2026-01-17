"""Support cases endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID

from src.infrastructure.auth.auth_middleware import get_current_user
from src.application.services.support_case_service import SupportCaseService
from src.domain.repositories.support_case_repository import (
    SQLAlchemySupportCaseRepository,
)
from src.infrastructure.database.database import get_db_session

router = APIRouter(prefix="/support-cases", tags=["Support Cases"])


@router.get("/", response_model=List)
async def get_support_cases(
    current_user=Depends(get_current_user), db=Depends(get_db_session)
):
    """Get user's support cases."""
    repository = SQLAlchemySupportCaseRepository(db)
    service = SupportCaseService(repository)

    # Get cases for current customer
    customer_id = UUID(
        current_user.get("customer_id")
    )  # Assuming JWT contains customer_id
    cases = service.get_customer_support_cases(customer_id)

    return cases


@router.post("/")
async def create_support_case(
    request: dict, current_user=Depends(get_current_user), db=Depends(get_db_session)
):
    """Create a new support case."""
    repository = SQLAlchemySupportCaseRepository(db)
    service = SupportCaseService(repository)

    # Add customer ID from authenticated user
    request["customer_id"] = current_user.get("customer_id")

    try:
        result = service.create_support_case(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{case_id}")
async def get_specific_support_case(
    case_id: str, current_user=Depends(get_current_user), db=Depends(get_db_session)
):
    """Get specific support case."""
    repository = SQLAlchemySupportCaseRepository(db)
    service = SupportCaseService(repository)

    try:
        result = service.get_support_case(UUID(case_id))
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{case_id}/status")
async def patch_support_case_status(
    case_id: str,
    request: dict,
    current_user=Depends(get_current_user),
    db=Depends(get_db_session),
):
    """Update support case status."""
    repository = SQLAlchemySupportCaseRepository(db)
    service = SupportCaseService(repository)

    status = request.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Status is required")

    try:
        result = service.update_support_case_status(UUID(case_id), status)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
