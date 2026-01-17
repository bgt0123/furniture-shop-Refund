"""Unit tests for refund amount calculation logic."""

import pytest

from src.domain.value_objects.refund_item import RefundItem
from src.application.services.refund_calculation_service import RefundCalculationService


class TestRefundCalculation:
    """Tests for refund calculation logic."""

    def test_calculate_total_refund_amount_single_item(self):
        """Test calculation of total refund amount for single item."""
        service = RefundCalculationService()

        items = [
            {
                "product_name": "Office Chair",
                "requested_quantity": 1,
                "original_unit_price": "150.00",
            }
        ]

        # This should fail initially since the service doesn't exist
        total_amount = service.calculate_total_amount(items)
        assert total_amount == 150.00

    def test_calculate_total_refund_amount_multiple_items(self):
        """Test calculation of total refund amount for multiple items."""
        service = RefundCalculationService()

        items = [
            {
                "product_name": "Office Chair",
                "requested_quantity": 2,
                "original_unit_price": "150.00",
            },
            {
                "product_name": "Desk",
                "requested_quantity": 1,
                "original_unit_price": "300.00",
            },
        ]

        # This should fail initially since the service doesn't exist
        total_amount = service.calculate_total_amount(items)
        assert total_amount == 600.00  # (2 * 150) + (1 * 300)

    def test_validate_14_day_delivery_window_valid(self):
        """Test validation of 14-day delivery window (valid case)."""
        service = RefundCalculationService()

        # Delivery date within 14 days
        delivery_date = "2024-01-01T00:00:00"
        current_date = "2024-01-15T00:00:00"

        # This should fail initially since the service doesn't exist
        is_valid = service.validate_delivery_window(delivery_date, current_date)
        assert is_valid is True

    def test_validate_14_day_delivery_window_expired(self):
        """Test validation of 14-day delivery window (expired case)."""
        service = RefundCalculationService()

        # Delivery date more than 14 days ago
        delivery_date = "2024-01-01T00:00:00"
        current_date = "2024-01-16T00:00:00"

        # This should fail initially since the service doesn't exist
        is_valid = service.validate_delivery_window(delivery_date, current_date)
        assert is_valid is False
