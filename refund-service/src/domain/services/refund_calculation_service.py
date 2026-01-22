from decimal import Decimal
from typing import Dict, List
from ..refund_request import RefundRequest
from ..refund_response import RefundMethod
from ..value_objects.money import Money


class RefundCalculationService:
    """Domain service for calculating refund amounts based on various factors"""

    @staticmethod
    def calculate_refund_amount(
        refund_request: RefundRequest,
        product_prices: Dict[str, float],
        is_defective: bool,
        delivery_days_since: int,
        refund_method: RefundMethod
    ) -> Money:
        """Calculate refund amount considering product condition, time, and method"""
        # Convert product prices to Decimal
        decimal_prices = {k: Decimal(str(v)) for k, v in product_prices.items()}
        
        base_amount = Decimal('0.0')
        
        # Calculate base amount from product prices
        for product_id in refund_request.product_ids:
            price = decimal_prices.get(product_id, Decimal('0.0'))
            
            # Determine refund multiplier based on defect status
            if is_defective:
                # Full refund for defective products
                refund_multiplier = Decimal('1.0')
            else:
                # Reduced refund for non-defective products
                refund_multiplier = Decimal('0.8')
            
            base_amount += price * refund_multiplier
        
        # Apply penalty based on days since delivery
        penalty_multiplier = RefundCalculationService._get_penalty_multiplier(delivery_days_since)
        
        # Apply method-specific adjustments
        method_multiplier = RefundCalculationService._get_method_multiplier(refund_method)
        
        final_amount = base_amount * penalty_multiplier * method_multiplier
        
        # Ensure amount doesn't exceed original purchase total
        purchase_total = RefundCalculationService._calculate_purchase_total(refund_request.product_ids, decimal_prices)
        final_amount = min(final_amount, purchase_total)
        
        return Money(final_amount, "USD")

    @staticmethod
    def _get_penalty_multiplier(delivery_days_since: int) -> Decimal:
        """Calculate penalty multiplier based on days since delivery"""
        if delivery_days_since <= 7:
            return Decimal('1.0')  # Full amount up to 7 days
        elif delivery_days_since <= 14:
            return Decimal('0.9')  # 10% penalty between 8-14 days
        elif delivery_days_since <= 30:
            return Decimal('0.7')  # 30% penalty between 15-30 days
        else:
            return Decimal('0.5')  # 50% penalty after 30 days

    @staticmethod
    def _get_method_multiplier(refund_method: RefundMethod) -> Decimal:
        """Get multiplier based on refund method"""
        multipliers = {
            RefundMethod.MONEY: Decimal('1.0'),     # Full amount
            RefundMethod.VOUCHER: Decimal('1.1'),   # Bonus 10% for voucher
            RefundMethod.REPLACEMENT: Decimal('1.0') # Full value for replacement
        }
        return multipliers.get(refund_method, Decimal('1.0'))

    @staticmethod
    def _calculate_purchase_total(product_ids: List[str], product_prices: Dict[str, Decimal]) -> Decimal:
        """Calculate total purchase amount for the products"""
        total = Decimal('0.0')
        for product_id in product_ids:
            total += product_prices.get(product_id, Decimal('0.0'))
        return total

    @staticmethod
    def get_product_prices_from_mock_data(product_ids: List[str]) -> Dict[str, float]:
        """Get product prices from mock data"""
        # Mock product prices based on product IDs
        mock_prices = {
            "PRD-001": 199.99,
            "PRD-002": 299.99,
            "PRD-003": 399.99,
            "PRD-004": 599.99,
            "PRD-005": 149.99,
            "PRD-006": 249.99,
            "PRD-007": 349.99,
            "PRD-008": 449.99,
            "PRD-009": 129.99,
            "PRD-010": 199.99
        }
        
        return {pid: mock_prices.get(pid, 100.00) for pid in product_ids}

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