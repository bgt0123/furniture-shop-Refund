"""Create Refund Case use case."""

from typing import Dict, Any
from uuid import uuid4, UUID
from datetime import datetime

from ...domain.entities.refund_case_domain import RefundCase, RefundItem, RefundStatus
from ...domain.repositories.refund_case_repository import RefundCaseRepository
from ...application.services.refund_calculation_service import RefundCalculationService


class CreateRefundCase:
    """Use case for creating a new refund case."""

    def __init__(self, repository: RefundCaseRepository):
        self.repository = repository

    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the create refund case use case."""

        # Validate required fields
        required_fields = ["support_case_id", "items", "delivery_date"]
        for field in required_fields:
            if field not in request:
                raise ValueError(f"Missing required field: {field}")

        if not request["items"]:
            raise ValueError("At least one refund item is required")

        # Parse delivery date
        try:
            delivery_date = datetime.fromisoformat(request["delivery_date"])
        except (ValueError, TypeError):
            raise ValueError("Invalid delivery date format")

        # Create refund items
        refund_items = []
        for item_data in request["items"]:
            try:
                item_required_fields = [
                    "product_id",
                    "product_name",
                    "requested_quantity",
                    "original_unit_price",
                ]
                for field in item_required_fields:
                    if field not in item_data:
                        raise ValueError(f"Missing required item field: {field}")

                item = RefundItem(
                    product_id=item_data["product_id"],
                    product_name=item_data["product_name"],
                    requested_quantity=int(item_data["requested_quantity"]),
                    original_unit_price=float(item_data["original_unit_price"]),
                )
                refund_items.append(item)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid item data: {str(e)}")

        # Calculate total amount
        calculation_service = RefundCalculationService()
        total_amount = calculation_service.calculate_total_amount(request["items"])

        # Check 14-day delivery window
        if not calculation_service.validate_delivery_window(request["delivery_date"]):
            raise ValueError("Refund request exceeds 14-day delivery window")

        # Create the refund case
        refund_id = uuid4()
        now = datetime.now()

        refund_case = RefundCase(
            refund_id=refund_id,
            support_case_id=UUID(request["support_case_id"]),
            items=refund_items,
            status=RefundStatus.PENDING,
            requested_amount=total_amount,
            delivery_date=delivery_date,
            refund_requested_at=now,
        )

        # Save to repository
        self.repository.save(refund_case)

        # Return result
        return {
            "refund_id": str(refund_id),
            "support_case_id": str(request["support_case_id"]),
            "status": "pending",
            "requested_amount": total_amount,
            "delivery_date": delivery_date.isoformat(),
            "refund_requested_at": now.isoformat(),
            "items": [
                {
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "requested_quantity": item.requested_quantity,
                    "original_unit_price": item.original_unit_price,
                    "total_refund_amount": item.total_refund_amount,
                }
                for item in refund_items
            ],
        }
