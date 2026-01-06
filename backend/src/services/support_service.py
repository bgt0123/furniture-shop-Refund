from typing import Optional, List, Dict, Any
from src.repositories.support_repository import support_case_repository
from src.models.support_case import SupportCase
from src.middleware.exceptions import (
    NotFoundException,
    BusinessRuleException,
    ValidationException,
)
from src.middleware.auth import auth_required, customer_only
from src.cache import cache
import logging

logger = logging.getLogger(__name__)


class SupportCaseService:
    def __init__(self):
        self.repository = support_case_repository

    def create_support_case(
        self,
        customer_id: str,
        order_id: str,
        issue_description: str,
        products: List[Dict[str, Any]],
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> SupportCase:
        """Create a new support case with validation"""
        try:
            # Validate input data
            self.repository.validate_case_creation(customer_id, order_id, products)

            # Create support case
            support_case = self.repository.create_support_case(
                customer_id, order_id, issue_description, products, attachments
            )

            # Clear cache for customer's support cases
            cache.delete(f"support_cases:{customer_id}")

            logger.info(f"Support case created: {support_case.id}")
            return support_case
        except Exception as e:
            logger.error(f"Error creating support case: {str(e)}")
            raise

    def get_support_case(self, case_id: str, customer_id: str) -> SupportCase:
        """Get support case by ID with customer access control"""
        try:
            support_case = self.repository.find_by_id(case_id)
            if not support_case:
                raise NotFoundException("SupportCase", f"ID {case_id}")

            # Check if customer has access to this case
            if support_case.customer_id != customer_id:
                raise BusinessRuleException(
                    "Access denied: Customer does not own this support case"
                )

            return support_case
        except Exception as e:
            logger.error(f"Error getting support case {case_id}: {str(e)}")
            raise

    def get_customer_support_cases(
        self, customer_id: str, status: Optional[str] = None
    ) -> List[SupportCase]:
        """Get all support cases for a customer"""
        try:
            cache_key = f"support_cases:{customer_id}:{status or 'all'}"

            # Try to get from cache
            cached_cases = cache.get(cache_key)
            if cached_cases:
                return cached_cases

            # Get from database
            cases = self.repository.find_by_customer(customer_id)

            # Filter by status if provided
            if status:
                cases = [case for case in cases if case.status == status]

            # Cache the results
            cache.set(cache_key, cases)

            return cases
        except Exception as e:
            logger.error(
                f"Error getting support cases for customer {customer_id}: {str(e)}"
            )
            raise

    def get_open_support_cases(self, customer_id: str) -> List[SupportCase]:
        """Get open support cases for a customer"""
        return self.get_customer_support_cases(customer_id, "Open")

    def close_support_case(self, case_id: str, customer_id: str) -> SupportCase:
        """Close a support case"""
        try:
            # Get the case and verify access
            support_case = self.get_support_case(case_id, customer_id)

            # Close the case
            closed_case = self.repository.close_case(case_id, customer_id)

            # Clear cache
            cache.delete(f"support_cases:{customer_id}")
            cache.delete(f"support_case:{case_id}")

            logger.info(f"Support case closed: {case_id}")
            return closed_case
        except Exception as e:
            logger.error(f"Error closing support case {case_id}: {str(e)}")
            raise

    def add_attachment_to_case(
        self, case_id: str, customer_id: str, attachment: Dict[str, Any]
    ) -> SupportCase:
        """Add attachment to support case"""
        try:
            # Get the case and verify access
            support_case = self.get_support_case(case_id, customer_id)

            # Add attachment
            updated_case = self.repository.add_attachment(case_id, attachment)

            # Clear cache
            cache.delete(f"support_case:{case_id}")

            logger.info(f"Attachment added to support case {case_id}")
            return updated_case
        except Exception as e:
            logger.error(f"Error adding attachment to support case {case_id}: {str(e)}")
            raise

    def validate_refund_eligibility(
        self, case_id: str, customer_id: str, product_ids: List[str]
    ) -> Dict[str, Any]:
        """Validate if products in support case are eligible for refund"""
        try:
            support_case = self.get_support_case(case_id, customer_id)

            # Get order details (this would be from order service in real implementation)
            # For now, we'll use mock data
            order_products = []
            for product in support_case.products:
                if product["product_id"] in product_ids:
                    order_products.append(
                        {
                            "product_id": product["product_id"],
                            "eligible": True,  # Mock eligibility
                            "delivery_date": "2026-01-01",  # Mock date
                            "reason": "Within 14-day window",
                        }
                    )

            return {
                "case_id": case_id,
                "eligible_products": order_products,
                "all_eligible": True,  # Mock response
            }
        except Exception as e:
            logger.error(
                f"Error validating refund eligibility for case {case_id}: {str(e)}"
            )
            raise


# Singleton instance
support_case_service = SupportCaseService()
