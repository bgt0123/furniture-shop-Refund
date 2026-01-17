"""Create Support Case use case."""

from typing import Dict, Any
from uuid import uuid4, UUID
from datetime import datetime

from ...domain.entities.support_case import SupportCase
from ...domain.repositories.support_case_repository import SupportCaseRepository


class CreateSupportCase:
    """Use case for creating a new support case."""

    def __init__(self, repository: SupportCaseRepository):
        self.repository = repository

    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the create support case use case."""

        # Validate required fields
        required_fields = ["customer_id", "order_id", "title", "description"]
        for field in required_fields:
            if field not in request:
                raise ValueError(f"Missing required field: {field}")

        # Create the support case
        case_id = uuid4()
        now = datetime.now()

        support_case = SupportCase(
            case_id=case_id,
            customer_id=UUID(request["customer_id"]),
            order_id=UUID(request["order_id"]),
            title=request["title"],
            description=request["description"],
            status="open",
            created_at=now,
            updated_at=now,
        )

        # Save to repository
        self.repository.save(support_case)

        # Return result
        return {
            "case_id": str(case_id),
            "customer_id": str(request["customer_id"]),
            "order_id": str(request["order_id"]),
            "title": request["title"],
            "description": request["description"],
            "status": "open",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
