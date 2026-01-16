from typing import List, Optional, Dict, Any
from uuid import UUID
from src.models.refund_case import RefundCase, RefundCaseStatus
from src.models.refund_eligibility import RefundEligibility, EligibilityStatus
from src.repositories.refund_repository import RefundCaseRepository
from src.utils.logging import logger
from src.services.support_case_service import SupportCaseService


class RefundCaseService:
    """Service for refund case operations."""

    def __init__(self, repository: Optional[RefundCaseRepository] = None):
        self.repository = repository or RefundCaseRepository()

    def create_refund_case(
        self,
        support_case_id: UUID,
        customer_id: UUID,
        order_id: str,
        products: List[Dict[str, Any]],
        reason: str,
    ) -> RefundCase:
        """Create a new refund case."""
        logger.info(
            f"Creating refund case for support case {support_case_id} and customer {customer_id}"
        )

        # Check if support case exists and is not closed
        support_case_service = SupportCaseService()
        support_case = support_case_service.get_support_case(support_case_id)

        if not support_case:
            raise ValueError(f"Support case {support_case_id} not found")

        if support_case.status == "Closed":
            raise ValueError(
                f"Cannot create refund for closed support case {support_case_id}"
            )

        # Check for existing refund cases for the same products in the same order
        existing_refunds = self.repository.get_by_support_case(str(support_case_id))

        # Check if any products in this refund request are already in existing refunds
        for refund in existing_refunds:
            for product in products:
                product_id = product.get("id")
                if any(
                    refund_product.get("id") == product_id
                    for refund_product in refund.products
                ):
                    raise ValueError(
                        f"Product {product_id} already has a refund case in support case {support_case_id}"
                    )

        # Calculate eligibility
        eligibility_result = self._calculate_eligibility(products)
        total_refund_amount = self._calculate_total_refund_amount(products)

        refund_case = RefundCase(
            support_case_id=str(support_case_id),
            customer_id=str(customer_id),
            order_id=str(order_id),
            products=products,
            total_refund_amount=total_refund_amount,
            status=RefundCaseStatus.PENDING,
            eligibility_status=eligibility_result.status,
            reason=reason,
        )

        return self.repository.create(refund_case)

    def get_refund_case(self, refund_id: UUID) -> Optional[RefundCase]:
        """Get refund case by ID."""
        logger.info(f"Getting refund case {refund_id}")
        return self.repository.get_by_id(str(refund_id))

    def get_customer_refund_cases(self, customer_id: UUID) -> List[RefundCase]:
        """Get all refund cases for a customer."""
        logger.info(f"Getting refund cases for customer {customer_id}")
        return self.repository.get_by_customer(str(customer_id))

    def get_refund_cases_by_support_case(
        self, support_case_id: UUID
    ) -> List[RefundCase]:
        """Get all refund cases for a support case."""
        logger.info(f"Getting refund cases for support case {support_case_id}")
        return self.repository.get_by_support_case(str(support_case_id))

    def get_all_refund_cases(self) -> List[RefundCase]:
        """Get all refund cases."""
        logger.info("Getting all refund cases")
        return self.repository.get_all()

    def get_refund_cases_by_status(self, status: str) -> List[RefundCase]:
        """Get all refund cases by status."""
        logger.info(f"Getting refund cases with status {status}")
        return self.repository.get_by_status(status)

    def approve_refund_case(
        self, refund_id: UUID, agent_id: UUID
    ) -> Optional[RefundCase]:
        """Approve a refund case."""
        logger.info(f"Approving refund case {refund_id} by agent {agent_id}")
        refund_case = self.repository.get_by_id(str(refund_id))

        if refund_case and refund_case.status == RefundCaseStatus.PENDING:
            refund_case.approve(agent_id)
            return self.repository.update(refund_case)

        return None

    def reject_refund_case(
        self, refund_id: UUID, agent_id: UUID, reason: str
    ) -> Optional[RefundCase]:
        """Reject a refund case."""
        logger.info(f"Rejecting refund case {refund_id} by agent {agent_id}")
        refund_case = self.repository.get_by_id(str(refund_id))

        if refund_case and refund_case.status == RefundCaseStatus.PENDING:
            refund_case.reject(agent_id, reason)
            return self.repository.update(refund_case)

        return None

    def complete_refund_case(self, refund_id: UUID) -> Optional[RefundCase]:
        """Mark refund case as completed."""
        logger.info(f"Completing refund case {refund_id}")
        refund_case = self.repository.get_by_id(str(refund_id))

        if refund_case:
            refund_case.complete()
            return self.repository.update(refund_case)

        return None

    def _calculate_eligibility(
        self, products: List[Dict[str, Any]]
    ) -> RefundEligibility:
        """Calculate eligibility for products."""
        from datetime import datetime

        # Convert products to eligibility info format
        eligibility_info = []
        for product in products:
            delivery_date_str = product.get("delivery_date")
            price = float(product.get("price", 0))
            quantity = product.get("quantity", 1)

            if delivery_date_str:
                try:
                    delivery_date = datetime.strptime(
                        delivery_date_str, "%Y-%m-%d"
                    ).date()
                    eligibility_info.append(
                        {
                            "delivery_date": delivery_date,
                            "price": price,
                            "quantity": quantity,
                        }
                    )
                except ValueError:
                    # If date parsing fails, use current date (will be treated as eligible)
                    eligibility_info.append(
                        {
                            "delivery_date": datetime.utcnow().date(),
                            "price": price,
                            "quantity": quantity,
                        }
                    )
            else:
                # No delivery date provided, treat as eligible
                eligibility_info.append(
                    {
                        "delivery_date": datetime.utcnow().date(),
                        "price": price,
                        "quantity": quantity,
                    }
                )

        return RefundEligibility.calculate_eligibility_for_products(
            products=eligibility_info, days_threshold=14
        )

    def _calculate_total_refund_amount(self, products: List[Dict[str, Any]]) -> float:
        """Calculate total refund amount."""
        total = 0.0
        for product in products:
            price = float(product.get("price", 0))
            quantity = product.get("quantity", 1)
            total += price * quantity
        return total
