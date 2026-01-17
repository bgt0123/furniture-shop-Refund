"""Unit tests for refund eligibility calculation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from uuid import uuid4
from datetime import datetime, timedelta
from models.refund_eligibility import RefundEligibility


class TestRefundEligibility:
    """Unit tests for refund eligibility calculation."""

    def test_eligible_within_14_days(self):
        """Test that products within 14-day window are eligible."""
        delivery_date = datetime.now() - timedelta(days=10)
        request_date = datetime.now()

        eligibility = RefundEligibility.calculate_eligibility(
            delivery_date, request_date
        )

        assert eligibility["eligible"] is True
        assert "within 14-day window" in eligibility["reason"]

    def test_ineligible_after_14_days(self):
        """Test that products after 14-day window are ineligible."""
        delivery_date = datetime.now() - timedelta(days=20)
        request_date = datetime.now()

        eligibility = RefundEligibility.calculate_eligibility(
            delivery_date, request_date
        )

        assert eligibility["eligible"] is False
        assert "days over" in eligibility["reason"]

    def test_eligible_on_exactly_14_days(self):
        """Test that products on exactly 14 days are eligible."""
        delivery_date = datetime.now() - timedelta(days=14)
        request_date = datetime.now()

        eligibility = RefundEligibility.calculate_eligibility(
            delivery_date, request_date
        )

        assert eligibility["eligible"] is True
        assert "within 14-day window" in eligibility["reason"]

    def test_ineligible_after_14_days_one_day(self):
        """Test that products after 14+1 days are ineligible."""
        delivery_date = datetime.now() - timedelta(days=15)
        request_date = datetime.now()

        eligibility = RefundEligibility.calculate_eligibility(
            delivery_date, request_date
        )

        assert eligibility["eligible"] is False
        assert "days over" in eligibility["reason"]

    def test_edge_case_time_of_day(self):
        """Test eligibility calculation considers time of day."""
        # Delivery at 10 AM
        delivery_date = datetime.now().replace(hour=10, minute=0, second=0) - timedelta(
            days=14
        )
        # Request at 2 PM same day (should still be eligible)
        request_date = datetime.now().replace(hour=14, minute=0, second=0)

        eligibility = RefundEligibility.calculate_eligibility(
            delivery_date, request_date
        )

        assert eligibility["eligible"] is True

    def test_multiple_products_mixed_eligibility(self):
        """Test eligibility calculation for multiple products."""
        products = [
            {
                "product_id": str(uuid4()),
                "quantity": 1,
                "price": 100.00,
                "delivery_date": datetime.now() - timedelta(days=5),
            },
            {
                "product_id": str(uuid4()),
                "quantity": 2,
                "price": 50.00,
                "delivery_date": datetime.now() - timedelta(days=20),
            },
        ]

        # Calculate eligibility for each product
        eligibility_results = []
        for product in products:
            eligibility = RefundEligibility.calculate_eligibility(
                product["delivery_date"], datetime.now()
            )
            eligibility_results.append(
                {
                    "product_id": product["product_id"],
                    "eligible": eligibility["eligible"],
                    "reason": eligibility["reason"],
                }
            )

        # First product should be eligible, second ineligible
        assert eligibility_results[0]["eligible"] is True
        assert eligibility_results[1]["eligible"] is False

    def test_weekends_and_holidays_handling(self):
        """Test that weekends and holidays don't extend the window."""
        # The 14-day window should be calendar days, not business days
        # This tests that weekends/holidays don't affect the calculation

        # Delivery date
        delivery_date = datetime.now().replace(hour=12, minute=0) - timedelta(days=20)

        # Request date 6 days after window
        request_date = delivery_date + timedelta(days=20)

        eligibility = RefundEligibility.calculate_eligibility(
            delivery_date, request_date
        )

        assert eligibility["eligible"] is False
        assert "days over" in eligibility["reason"]
