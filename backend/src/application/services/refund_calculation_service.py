"""Refund Calculation Service for business logic around refund calculations."""

from datetime import datetime


class RefundCalculationService:
    """Service for refund calculation business logic."""

    def calculate_total_amount(self, items: list) -> float:
        """Calculate total refund amount from items."""
        total = 0.0
        for item in items:
            try:
                quantity = int(item.get("requested_quantity", 0))
                unit_price = float(item.get("original_unit_price", 0))
                total += quantity * unit_price
            except (ValueError, TypeError):
                raise ValueError(f"Invalid item data: {item}")

        return round(total, 2)

    def validate_delivery_window(
        self, delivery_date_str: str, current_date: datetime = None
    ) -> bool:
        """Validate if delivery date is within 14-day refund window."""
        try:
            delivery_date = datetime.fromisoformat(
                delivery_date_str.replace("Z", "+00:00")
            )
        except (ValueError, TypeError):
            raise ValueError("Invalid delivery date format")

        if current_date is None:
            current_date = datetime.now()

        time_delta = current_date - delivery_date
        return time_delta.days <= 14

    def calculate_item_amount(self, quantity: int, unit_price: float) -> float:
        """Calculate refund amount for a single item."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if unit_price <= 0:
            raise ValueError("Unit price must be positive")

        return round(quantity * unit_price, 2)

    def is_partial_refund_possible(self, total_items: list, refund_items: list) -> bool:
        """Check if partial refund is possible based on item quantities."""
        # Build order quantity mapping
        order_quantities = {}
        for item in total_items:
            product_id = item.get("product_id")
            quantity = int(item.get("quantity", 0))
            if product_id:
                order_quantities[product_id] = quantity

        # Check refund quantities
        for refund_item in refund_items:
            product_id = refund_item.get("product_id")
            refund_quantity = int(refund_item.get("requested_quantity", 0))

            if product_id not in order_quantities:
                return False

            if refund_quantity > order_quantities[product_id]:
                return False

        return True
