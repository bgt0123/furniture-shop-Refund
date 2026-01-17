"""Delivery window validator value object."""

from datetime import datetime, timedelta
from typing import Optional


class DeliveryWindowValidator:
    """Validates refund approval windows based on delivery dates."""

    def __init__(self, delivery_date: datetime):
        """Initialize with delivery date.

        Args:
            delivery_date: The date when the order was delivered.

        Raises:
            ValueError: If delivery_date is None
        """
        if delivery_date is None:
            raise ValueError("Delivery date cannot be None")
        self.delivery_date = delivery_date

    def is_within_14_days(self, current_date: datetime) -> bool:
        """Check if current date is within 14 days of delivery.

        Args:
            current_date: The date to check against delivery date.

        Returns:
            bool: True if current_date is within 14 days of delivery_date
        """
        if current_date is None:
            return False

        days_difference = (current_date - self.delivery_date).days
        return 0 <= days_difference <= 14
