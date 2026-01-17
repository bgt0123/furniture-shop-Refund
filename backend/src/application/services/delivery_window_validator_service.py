"""Service for delivery window validation."""

from datetime import datetime

from src.domain.value_objects.delivery_window_validator import DeliveryWindowValidator


class DeliveryWindowValidatorService:
    """Service for validating 14-day delivery window for refunds."""

    def validate_refund_window(
        self, delivery_date: datetime, current_date: datetime
    ) -> bool:
        """Validate if current date is within 14 days of delivery.

        Args:
            delivery_date: Date when order was delivered
            current_date: Current date for validation

        Returns:
            True if within 14-day window, False otherwise
        """
        validator = DeliveryWindowValidator(delivery_date)
        return validator.is_within_14_days(current_date)

    def get_days_remaining(
        self, delivery_date: datetime, current_date: datetime
    ) -> int:
        """Get number of days remaining in refund window.

        Args:
            delivery_date: Date when order was delivered
            current_date: Current date for calculation

        Returns:
            Number of days remaining (negative if expired)
        """
        days_since_delivery = (current_date - delivery_date).days
        return max(0, 14 - days_since_delivery)
