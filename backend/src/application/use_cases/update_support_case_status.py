"""Update Support Case Status use case."""

from typing import Dict, Any
from uuid import UUID

from ...domain.repositories.support_case_repository import SupportCaseRepository


class UpdateSupportCaseStatus:
    """Use case for updating support case status."""

    def __init__(self, repository: SupportCaseRepository):
        self.repository = repository

    def execute(self, case_id: UUID, status: str) -> Dict[str, Any]:
        """Execute the update support case status use case."""

        # Validate status
        valid_statuses = ["open", "in_progress", "resolved", "closed"]
        if status not in valid_statuses:
            raise ValueError(
                f"Invalid status: {status}. Must be one of {valid_statuses}"
            )

        # Update status
        success = self.repository.update_status(case_id, status)

        if not success:
            raise ValueError(f"Support case with ID {case_id} not found")

        # Return updated case info - success flag already handled
        # If we got here, the update was successful
        return {"case_id": str(case_id), "status": status, "updated": True}
