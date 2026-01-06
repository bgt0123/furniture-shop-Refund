from typing import Optional, List, Dict, Any
from src.repositories.base_repository import BaseRepository
from src.models.support_case import SupportCase
from src.middleware.exceptions import (
    NotFoundException,
    BusinessRuleException,
    ValidationException,
)
from datetime import datetime
import uuid


class SupportCaseRepository(BaseRepository[SupportCase]):
    def __init__(self):
        super().__init__(SupportCase)

    def create_support_case(
        self,
        customer_id: str,
        order_id: str,
        issue_description: str,
        products: List[Dict[str, Any]],
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> SupportCase:
        """Create a new support case"""
        case = SupportCase.create_from_data(
            customer_id, order_id, issue_description, products, attachments
        )
        return self.create(case)

    def find_by_customer(
        self, customer_id: str, skip: int = 0, limit: int = 100
    ) -> List[SupportCase]:
        """Find support cases by customer ID"""
        return self.find_all_by_field("customer_id", customer_id, skip, limit)

    def find_by_order(self, order_id: str) -> List[SupportCase]:
        """Find support cases by order ID"""
        return self.find_all_by_field("order_id", order_id)

    def find_open_cases_by_customer(self, customer_id: str) -> List[SupportCase]:
        """Find open support cases by customer ID"""
        with self.get_session() as session:
            from sqlalchemy import and_
            from src.models.support_case import SupportCaseStatus

            stmt = session.query(SupportCase).filter(
                and_(
                    SupportCase.customer_id == customer_id,
                    SupportCase.status == SupportCaseStatus.OPEN,
                )
            )
            result = session.execute(stmt)
            return result.scalars().all()

    def close_case(self, case_id: str, user_id: str) -> SupportCase:
        """Close a support case"""
        case = self.find_by_id(case_id)
        if not case:
            raise NotFoundException("SupportCase", f"ID {case_id}")

        if case.status != "Open":
            raise BusinessRuleException(
                "Case is not in Open status and cannot be closed"
            )

        # Check if case can be closed (no pending refunds)
        if not case.can_be_closed():
            raise BusinessRuleException(
                "Cannot close case with pending refund requests", {"case_id": case_id}
            )

        case.close_case()
        case.add_history_entry("case_closed", user_id, {"status": "Closed"})

        return self.update(case_id, case.to_dict())

    def add_attachment(self, case_id: str, attachment: Dict[str, Any]) -> SupportCase:
        """Add attachment to support case"""
        case = self.find_by_id(case_id)
        if not case:
            raise NotFoundException("SupportCase", f"ID {case_id}")

        current_attachments = case.attachments or []
        current_attachments.append(attachment)
        case.attachments = current_attachments
        case.add_history_entry(
            "attachment_added", "system", {"attachment_id": attachment["id"]}
        )

        return self.update(case_id, case.to_dict())

    def validate_case_creation(
        self, customer_id: str, order_id: str, products: List[Dict[str, Any]]
    ) -> None:
        """Validate support case creation data"""
        if not customer_id or not order_id:
            raise ValidationException("Customer ID and Order ID are required")

        if not issue_description or len(issue_description.strip()) < 10:
            raise ValidationException(
                "Issue description must be at least 10 characters"
            )

        if not products or len(products) == 0:
            raise ValidationException("At least one product must be specified")

        for product in products:
            if (
                not product.get("product_id")
                or not product.get("quantity")
                or product["quantity"] < 1
            ):
                raise ValidationException(
                    "Each product must have a valid product_id and quantity >= 1"
                )


# Singleton instance
support_case_repository = SupportCaseRepository()
