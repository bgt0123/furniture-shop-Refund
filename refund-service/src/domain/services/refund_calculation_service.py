from typing import List
from decimal import Decimal
from ..refund_request import RefundRequest
from ..refund_response import RefundMethod


class RefundCalculationService:
    """Domain service to calculate refund amounts based on products"""

    @staticmethod
    def calculate_refund_amount(
        refund_request: RefundRequest,
        product_prices: dict[str, Decimal]
    ) -> Decimal:
        """Calculate refund amount based on products and their prices"""
        
        total_amount = Decimal("0.0")
        
        for product_id in refund_request.product_ids:
            if product_id in product_prices:
                total_amount += product_prices[product_id]
        
        return total_amount

    @staticmethod
    def get_available_refund_methods(
        refund_amount: Decimal,
        product_categories: List[str]
    ) -> List[RefundMethod]:
        """Determine available refund methods based on amount and product types"""
        
        methods = [RefundMethod.MONEY, RefundMethod.VOUCHER]
        
        # For furniture products, also offer replacement
        if "furniture" in product_categories:
            methods.append(RefundMethod.REPLACEMENT)
        
        return methods