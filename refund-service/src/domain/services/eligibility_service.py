from datetime import datetime, timedelta
from decimal import Decimal
from typing import List
from ..refund_request import RefundRequest
from ..value_objects.refund_eligibility import RefundEligibility


class EligibilityService:
    """Domain service to validate refund eligibility against business rules"""

    @staticmethod
    def determine_eligibility(
        refund_request: RefundRequest,
        order_delivery_date: str,
        product_condition: str,
        product_prices: dict
    ) -> RefundEligibility:
        """Determine refund eligibility based on multiple business rules"""
        reasons = []
        refund_amount = None
        eligibility_date = datetime.utcnow()

        # Rule 1: Check if product is defective
        is_defective = product_condition == "defective"
        if is_defective:
            reasons.append("Product is defective")

        # Rule 2: Check if within 14 days of delivery
        is_within_delivery_window = False
        try:
            delivery_date = datetime.fromisoformat(order_delivery_date)
            days_since_delivery = (eligibility_date - delivery_date).days
            is_within_delivery_window = days_since_delivery <= 14
            
            if is_within_delivery_window:
                reasons.append("Within 14-day delivery window")
            else:
                reasons.append(f"Delivery was {days_since_delivery} days ago (14-day limit)")
        except (ValueError, TypeError):
            reasons.append("Could not verify delivery date")

        # Rule 3: Check product existence in order
        has_valid_products = bool(refund_request.product_ids)
        if has_valid_products:
            reasons.append("Valid product IDs provided")
        else:
            reasons.append("No valid product IDs provided")

        # Rule 4: Check for duplicate products
        has_duplicates = len(refund_request.product_ids) != len(set(refund_request.product_ids))
        if has_duplicates:
            reasons.append("Duplicate products found in request")

        # Rule 5: Calculate refund amount
        if has_valid_products and not has_duplicates:
            refund_amount = EligibilityService._calculate_refund_amount(
                refund_request.product_ids,
                product_prices,
                is_defective
            )

        # Final eligibility determination
        is_eligible = (
            (is_defective or is_within_delivery_window) and
            has_valid_products and
            not has_duplicates
        )

        return RefundEligibility(
            is_eligible=is_eligible,
            reasons=reasons,
            calculated_refund_amount=refund_amount,
            eligibility_date=eligibility_date
        )

    @staticmethod
    def _calculate_refund_amount(
        product_ids: List[str],
        product_prices: dict,
        is_defective: bool
    ) -> Decimal:
        """Calculate refund amount based on product prices and condition"""
        total_amount = Decimal('0.0')
        
        for product_id in product_ids:
            price = Decimal(str(product_prices.get(product_id, 0.0)))
            
            # Apply discount logic based on defect status
            if is_defective:
                # Full refund for defective products
                refund_multiplier = Decimal('1.0')
            else:
                # Partial refund (80%) for non-defective products
                refund_multiplier = Decimal('0.8')
                
            product_refund = price * refund_multiplier
            total_amount += product_refund
        
        return total_amount