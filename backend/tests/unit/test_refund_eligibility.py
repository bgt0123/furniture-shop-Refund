import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import datetime, timedelta
from src.models.refund_eligibility import RefundEligibility, EligibilityStatus


class TestRefundEligibility:
    """Test refund eligibility calculation logic."""

    def test_eligibility_calculation_eligible(self):
        """Test eligibility calculation for eligible products."""
        # Product delivered within 14 days
        delivery_date = datetime.utcnow().date() - timedelta(days=5)
        product_price = 99.99
        quantity = 1

        eligibility = RefundEligibility.calculate_eligibility(
            delivery_date=delivery_date,
            product_price=product_price,
            quantity=quantity,
            days_threshold=14,
        )

        assert eligibility.status == EligibilityStatus.ELIGIBLE
        assert eligibility.refund_amount == product_price * quantity

    def test_eligibility_calculation_ineligible(self):
        """Test eligibility calculation for ineligible products."""
        # Product delivered beyond 14 days
        delivery_date = datetime.utcnow().date() - timedelta(days=20)
        product_price = 99.99
        quantity = 1

        eligibility = RefundEligibility.calculate_eligibility(
            delivery_date=delivery_date,
            product_price=product_price,
            quantity=quantity,
            days_threshold=14,
        )

        assert eligibility.status == EligibilityStatus.INELIGIBLE
        assert eligibility.refund_amount == 0.0

    def test_eligibility_on_threshold_boundary(self):
        """Test eligibility calculation exactly on the 14-day threshold."""
        # Product delivered exactly 14 days ago
        delivery_date = datetime.utcnow().date() - timedelta(days=14)
        product_price = 99.99
        quantity = 1

        eligibility = RefundEligibility.calculate_eligibility(
            delivery_date=delivery_date,
            product_price=product_price,
            quantity=quantity,
            days_threshold=14,
        )

        # Should be eligible (inclusive on threshold)
        assert eligibility.status == EligibilityStatus.ELIGIBLE
        assert eligibility.refund_amount == product_price * quantity

    def test_calculate_multiple_products(self):
        """Test eligibility calculation for multiple products."""
        product_list = [
            {
                "delivery_date": datetime.utcnow().date() - timedelta(days=5),
                "price": 99.99,
                "quantity": 1,
            },
            {
                "delivery_date": datetime.utcnow().date() - timedelta(days=20),
                "price": 199.99,
                "quantity": 2,
            },
            {
                "delivery_date": datetime.utcnow().date() - timedelta(days=3),
                "price": 49.99,
                "quantity": 1,
            },
        ]

        eligibility = RefundEligibility.calculate_eligibility_for_products(
            products=product_list, days_threshold=14
        )

        # Should be partially eligible
        assert eligibility.status == EligibilityStatus.PARTIALLY_ELIGIBLE
        # Only products delivered within 14 days should be refunded
        expected_amount = 99.99 + 49.99
        assert abs(eligibility.refund_amount - expected_amount) < 0.01

    def test_all_eligible_products(self):
        """Test when all products are eligible."""
        product_list = [
            {
                "delivery_date": datetime.utcnow().date() - timedelta(days=5),
                "price": 99.99,
                "quantity": 1,
            },
            {
                "delivery_date": datetime.utcnow().date() - timedelta(days=10),
                "price": 199.99,
                "quantity": 2,
            },
        ]

        eligibility = RefundEligibility.calculate_eligibility_for_products(
            products=product_list, days_threshold=14
        )

        assert eligibility.status == EligibilityStatus.ELIGIBLE
        expected_amount = 99.99 + (199.99 * 2)
        assert abs(eligibility.refund_amount - expected_amount) < 0.01

    def test_all_ineligible_products(self):
        """Test when all products are ineligible."""
        product_list = [
            {
                "delivery_date": datetime.utcnow().date() - timedelta(days=20),
                "price": 99.99,
                "quantity": 1,
            },
            {
                "delivery_date": datetime.utcnow().date() - timedelta(days=30),
                "price": 199.99,
                "quantity": 1,
            },
        ]

        eligibility = RefundEligibility.calculate_eligibility_for_products(
            products=product_list, days_threshold=14
        )

        assert eligibility.status == EligibilityStatus.INELIGIBLE
        assert eligibility.refund_amount == 0.0

    def test_future_delivery_date(self):
        """Test with future delivery date - should be eligible."""
        delivery_date = datetime.utcnow().date() + timedelta(days=5)
        product_price = 99.99

        eligibility = RefundEligibility.calculate_eligibility(
            delivery_date=delivery_date,
            product_price=product_price,
            quantity=1,
            days_threshold=14,
        )

        # Future date should be treated as eligible
        assert eligibility.status == EligibilityStatus.ELIGIBLE
        assert eligibility.refund_amount == product_price

    def test_custom_threshold(self):
        """Test with custom refund threshold."""
        delivery_date = datetime.utcnow().date() - timedelta(days=10)
        product_price = 99.99

        # With 10-day threshold, should be ineligible
        eligibility = RefundEligibility.calculate_eligibility(
            delivery_date=delivery_date,
            product_price=product_price,
            quantity=1,
            days_threshold=7,
        )

        assert eligibility.status == EligibilityStatus.INELIGIBLE

        # With 10-day threshold, should be eligible
        eligibility = RefundEligibility.calculate_eligibility(
            delivery_date=delivery_date,
            product_price=product_price,
            quantity=1,
            days_threshold=14,
        )

        assert eligibility.status == EligibilityStatus.ELIGIBLE

    def test_product_quantities(self):
        """Test with different product quantities."""
        delivery_date = datetime.utcnow().date() - timedelta(days=5)
        product_price = 50.0
        quantity = 3

        eligibility = RefundEligibility.calculate_eligibility(
            delivery_date=delivery_date,
            product_price=product_price,
            quantity=quantity,
            days_threshold=14,
        )

        assert eligibility.status == EligibilityStatus.ELIGIBLE
        assert eligibility.refund_amount == product_price * quantity

    def test_zero_amount_product(self):
        """Test with zero-priced product."""
        delivery_date = datetime.utcnow().date() - timedelta(days=5)
        product_price = 0.0
        quantity = 1

        eligibility = RefundEligibility.calculate_eligibility(
            delivery_date=delivery_date,
            product_price=product_price,
            quantity=quantity,
            days_threshold=14,
        )

        assert eligibility.status == EligibilityStatus.ELIGIBLE
        assert eligibility.refund_amount == 0.0
