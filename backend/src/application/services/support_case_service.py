"""Support Case Service for coordinating support case operations."""

from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime

from ..use_cases.create_support_case import CreateSupportCase
from ..use_cases.get_support_case import GetSupportCase
from ..use_cases.update_support_case_status import UpdateSupportCaseStatus
from ...domain.repositories.support_case_repository import SupportCaseRepository


class SupportCaseService:
    """Service layer for support case operations."""

    def __init__(self, repository: SupportCaseRepository):
        self.repository = repository
        self.create_case_use_case = CreateSupportCase(repository)
        self.get_case_use_case = GetSupportCase(repository)
        self.update_status_use_case = UpdateSupportCaseStatus(repository)

    def create_support_case(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new support case."""
        return self.create_case_use_case.execute(request)

    def get_support_case(self, case_id: UUID) -> Dict[str, Any]:
        """Get a support case by ID."""
        return self.get_case_use_case.execute(case_id)

    def update_support_case_status(self, case_id: UUID, status: str) -> Dict[str, Any]:
        """Update support case status."""
        return self.update_status_use_case.execute(case_id, status)

    def get_customer_support_cases(self, customer_id: UUID) -> List[Dict[str, Any]]:
        """Get all support cases for a customer."""
        cases = self.repository.find_by_customer_id(customer_id)

        return [
            {
                "case_id": str(case.case_id),
                "customer_id": str(case.customer_id),
                "order_id": str(case.order_id),
                "title": case.title,
                "description": case.description,
                "status": case.status,
                "created_at": case.created_at.isoformat(),
                "updated_at": case.updated_at.isoformat(),
            }
            for case in cases
        ]
