from typing import List
from ..refund_request import RefundRequest


class EligibilityService:
    """Domain service to validate refund eligibility against business rules"""

    @staticmethod
    def is_eligible_for_refund(
        refund_request: RefundRequest,
        order_delivery_date: str,
        is_product_defective: bool
    ) -> bool:
        """Check if refund request is eligible based on business rules"""
        
        # Must be within 14 days of delivery OR product defective
        # (This would normally involve date calculations)
        if is_product_defective:
            return True

        # Products must exist in referenced order
        if not refund_request.product_ids:
            return False

        # Cannot process already refunded products 
        # (This would check against a database of refunded products)
        
        return True

    @staticmethod
    def validate_no_duplicate_products(refund_request: RefundRequest) -> bool:
        """Ensure no duplicate products in the refund request"""
        if len(refund_request.product_ids) != len(set(refund_request.product_ids)):
            return False
        return True