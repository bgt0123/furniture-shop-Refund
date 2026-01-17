"""Unit tests for 14-day delivery window validation."""

import pytest
from datetime import datetime, timedelta

from src.domain.value_objects.delivery_window_validator import DeliveryWindowValidator


class TestDeliveryWindowValidator:
    """Test delivery window validation logic."""

    def test_valid_delivery_window_within_14_days(self):
        """Test that delivery dates within 14 days are valid."""
        delivery_date = datetime.now()
        validator = DeliveryWindowValidator(delivery_date)

        # Test dates within 14 days
        assert validator.is_within_14_days(delivery_date + timedelta(days=10)) == True
        assert validator.is_within_14_days(delivery_date + timedelta(days=14)) == True
        assert validator.is_within_14_days(delivery_date) == True

    def test_invalid_delivery_window_after_14_days(self):
        """Test that delivery dates after 14 days are invalid."""
        delivery_date = datetime.now()
        validator = DeliveryWindowValidator(delivery_date)

        # Test dates after 14 days
        assert validator.is_within_14_days(delivery_date + timedelta(days=15)) == False
        assert validator.is_within_14_days(delivery_date + timedelta(days=30)) == False

    def test_delivery_window_edge_case_time_boundaries(self):
        """Test edge cases around the 14-day boundary."""
        delivery_date = datetime(2023, 1, 1, 12, 0, 0)  # Jan 1, 2023 12:00 PM
        validator = DeliveryWindowValidator(delivery_date)

        # Exactly 14 days later - should be valid
        same_time_14_days_later = datetime(2023, 1, 15, 12, 0, 0)
        assert validator.is_within_14_days(same_time_14_days_later) == True

        # One minute after 14 days - should be invalid
        one_minute_after_14_days = datetime(2023, 1, 15, 12, 1, 0)
        assert validator.is_within_14_days(one_minute_after_14_days) == False

    def test_null_delivery_date_raises_error(self):
        """Test that None delivery date raises ValueError."""
        with pytest.raises(ValueError, match="Delivery date cannot be None"):
            DeliveryWindowValidator(None)
