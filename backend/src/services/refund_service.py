from typing import Optional, List, Dict, Any
from src.repositories.refund_repository import refund_case_repository
from src.repositories.support_repository import support_case_repository
from src.models.refund_case import RefundCase
from src.middleware.exceptions import (
    NotFoundException,
    BusinessRuleException,
    ValidationException,
)
from src.middleware.auth import auth_required, customer_only
from src.cache import cache
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RefundCaseService:
    def __init__(self):
        self.repository = refund_case_repository
        self.support_repository = support_case_repository

    def create_refund_request(
        self,
        support_case_id: str,
        customer_id: str,
        products: List[Dict[str, Any]],
        delivery_dates: Dict[str, str],
    ) -> RefundCase:
        """Create a refund request from a support case"""
        try:
            # Validate the refund request
            self.repository.validate_refund_request(
                support_case_id, customer_id, products
            )

            # Check if support case exists and belongs to customer
            support_case = self.support_repository.find_by_id(support_case_id)
            if not support_case:
                raise NotFoundException("SupportCase", f"ID {support_case_id}")

            if support_case.customer_id != customer_id:
                raise BusinessRuleException(
                    "Access denied: Customer does not own this support case"
                )

            if support_case.status != "Open":
                raise BusinessRuleException(
                    "Refund requests can only be created from open support cases"
                )

            # Check for existing refund requests on the same products
            conflict_check = self.repository.check_existing_refunds(
                support_case_id, [p["product_id"] for p in products]
            )
            if conflict_check["has_conflicts"]:
                raise BusinessRuleException(
                    "Some products already have active refund requests",
                    {"conflicts": conflict_check["conflicting_refunds"]},
                )

            # Create the refund case
            refund_case = self.repository.create_refund_case(
                support_case_id,
                customer_id,
                support_case.order_id,
                products,
                delivery_dates,
            )

            # Clear cache
            cache.delete(f"refund_cases:{customer_id}")
            cache.delete(f"support_case:{support_case_id}")

            logger.info(f"Refund request created: {refund_case.id}")
            return refund_case
        except Exception as e:
            logger.error(f"Error creating refund request: {str(e)}")
            raise

    def get_refund_case(self, refund_id: str, customer_id: str) -> RefundCase:
        """Get refund case by ID with customer access control"""
        try:
            refund_case = self.repository.find_by_id(refund_id)
            if not refund_case:
                raise NotFoundException("RefundCase", f"ID {refund_id}")

            # Check if customer has access to this refund case
            if refund_case.customer_id != customer_id:
                raise BusinessRuleException(
                    "Access denied: Customer does not own this refund case"
                )

            return refund_case
        except Exception as e:
            logger.error(f"Error getting refund case {refund_id}: {str(e)}")
            raise

    def get_customer_refund_cases(
        self, customer_id: str, status: Optional[str] = None
    ) -> List[RefundCase]:
        """Get all refund cases for a customer"""
        try:
            cache_key = f"refund_cases:{customer_id}:{status or 'all'}"

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
                f"Error getting refund cases for customer {customer_id}: {str(e)}"
            )
            raise

    def get_refund_cases_by_support_case(
        self, support_case_id: str, customer_id: str
    ) -> List[RefundCase]:
        """Get refund cases for a specific support case"""
        try:
            # Verify customer has access to the support case
            support_case = self.support_repository.find_by_id(support_case_id)
            if not support_case or support_case.customer_id != customer_id:
                raise BusinessRuleException(
                    "Access denied: Customer does not own this support case"
                )

            return self.repository.find_by_support_case(support_case_id)
        except Exception as e:
            logger.error(
                f"Error getting refund cases for support case {support_case_id}: {str(e)}"
            )
            raise

    def get_all_refund_cases_admin(
        self,
        status: Optional[str] = None,
        customer_id: Optional[str] = None,
    ) -> List[RefundCase]:
        """Get all refund cases for admin view"""
        try:
            cases = self.repository.find_all()

            # Filter by status if provided
            if status:
                cases = [case for case in cases if case.status == status]

            # Filter by customer if provided
            if customer_id:
                cases = [case for case in cases if case.customer_id == customer_id]

            return cases
        except Exception as e:
            logger.error(f"Error getting all refund cases for admin: {str(e)}")
            raise

    def get_refund_case_admin(self, refund_id: str) -> RefundCase:
        """Get refund case by ID for admin (no customer access control)"""
        try:
            refund_case = self.repository.find_by_id(refund_id)
            if not refund_case:
                raise NotFoundException("RefundCase", f"ID {refund_id}")

            return refund_case
        except Exception as e:
            logger.error(f"Error getting refund case {refund_id} for admin: {str(e)}")
            raise

    def approve_refund_case(self, refund_id: str, agent_id: str) -> RefundCase:
        """Approve a refund case"""
        try:
            refund_case = self.repository.find_by_id(refund_id)
            if not refund_case:
                raise NotFoundException("RefundCase", f"ID {refund_id}")

            # Validate that the refund case is pending
            if refund_case.status != "Pending":
                raise BusinessRuleException(
                    f"Refund case {refund_id} is not in Pending status (current: {refund_case.status})"
                )

            # Validate that the refund case is eligible
            if refund_case.eligibility_status != "Eligible":
                raise BusinessRuleException(
                    f"Refund case {refund_id} is not eligible for approval (status: {refund_case.eligibility_status})"
                )

            # Approve the refund
            refund_case.approve_refund(agent_id)

            # Update in repository
            updated_case = self.repository.update(refund_case)

            # Clear cache
            cache.delete(f"refund_case:{refund_id}")
            cache.delete(f"refund_cases:{refund_case.customer_id}")

            logger.info(f"Refund case {refund_id} approved by agent {agent_id}")
            return updated_case
        except Exception as e:
            logger.error(f"Error approving refund case {refund_id}: {str(e)}")
            raise

    def reject_refund_case(
        self, refund_id: str, agent_id: str, reason: str
    ) -> RefundCase:
        """Reject a refund case"""
        try:
            refund_case = self.repository.find_by_id(refund_id)
            if not refund_case:
                raise NotFoundException("RefundCase", f"ID {refund_id}")

            # Validate that the refund case is pending
            if refund_case.status != "Pending":
                raise BusinessRuleException(
                    f"Refund case {refund_id} is not in Pending status (current: {refund_case.status})"
                )

            # Reject the refund
            refund_case.reject_refund(agent_id, reason)

            # Update in repository
            updated_case = self.repository.update(refund_case)

            # Clear cache
            cache.delete(f"refund_case:{refund_id}")
            cache.delete(f"refund_cases:{refund_case.customer_id}")

            logger.info(
                f"Refund case {refund_id} rejected by agent {agent_id}: {reason}"
            )
            return updated_case
        except Exception as e:
            logger.error(f"Error rejecting refund case {refund_id}: {str(e)}")
            raise


# Singleton instance
refund_case_service = RefundCaseService()
