from typing import List, Optional, Dict, Any
from uuid import UUID
from models.support_case import SupportCase, SupportCaseStatus, RefundIntention
from repositories.support_repository import SupportCaseRepository
from utils.logging import logger


class SupportCaseService:
    """Service for support case operations."""

    def __init__(self, repository: Optional[SupportCaseRepository] = None):
        self.repository = repository or SupportCaseRepository()

    def create_support_case(
        self,
        customer_id: UUID,
        order_id: str,
        products: List[Dict[str, Any]],
        issue_description: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
        intends_refund: RefundIntention = RefundIntention.NO,
    ) -> SupportCase:
        """Create a new support case."""
        logger.info(
            f"Creating support case for customer {customer_id} and order {order_id}"
        )

        support_case = SupportCase(
            customer_id=str(customer_id),
            order_id=str(order_id),
            products=products,
            issue_description=issue_description,
            attachments=attachments or [],
            status=SupportCaseStatus.OPEN,
            intends_refund=intends_refund,
        )

        return self.repository.create(support_case)

    def get_support_case(self, case_id: UUID) -> Optional[SupportCase]:
        """Get support case by ID."""
        logger.info(f"Getting support case {case_id}")
        return self.repository.get_by_id(str(case_id))

    def get_customer_support_cases(self, customer_id: UUID) -> List[SupportCase]:
        """Get all support cases for a customer."""
        logger.info(f"Getting support cases for customer {customer_id}")
        return self.repository.get_by_customer(str(customer_id))

    def close_support_case(self, case_id: UUID) -> Optional[SupportCase]:
        """Close a support case."""
        logger.info(f"Closing support case {case_id}")
        support_case = self.repository.get_by_id(str(case_id))

        if support_case and support_case.can_close():
            support_case.close()
            return self.repository.update(support_case)

        return None

    def add_attachment(
        self, case_id: UUID, attachment: Dict[str, Any]
    ) -> Optional[SupportCase]:
        """Add attachment to support case."""
        logger.info(f"Adding attachment to support case {case_id}")
        support_case = self.repository.get_by_id(str(case_id))

        if support_case:
            support_case.add_attachment(attachment)
            return self.repository.update(support_case)

        return None
