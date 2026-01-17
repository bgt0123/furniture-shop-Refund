"""Get Support Case use case."""

from typing import Dict, Any
from uuid import UUID

from ...domain.repositories.support_case_repository import SupportCaseRepository


class GetSupportCase:
    """Use case for retrieving a support case."""

    def __init__(self, repository: SupportCaseRepository):
        self.repository = repository

    def execute(self, case_id: UUID) -> Dict[str, Any]:
        """Execute the get support case use case."""

        support_case = self.repository.find_by_id(case_id)

        if not support_case:
            raise ValueError(f"Support case with ID {case_id} not found")

        # Convert to dictionary
        return {
            "case_id": str(support_case.case_id),
            "customer_id": str(support_case.customer_id),
            "order_id": str(support_case.order_id),
            "title": support_case.title,
            "description": support_case.description,
            "status": support_case.status,
            "created_at": support_case.created_at.isoformat(),
            "updated_at": support_case.updated_at.isoformat(),
        }
