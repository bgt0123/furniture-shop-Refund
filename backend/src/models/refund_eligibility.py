from datetime import datetime, date
from typing import List, Dict, Any, TypedDict
from dataclasses import dataclass
from enum import Enum


class EligibilityStatus(str, Enum):
    """Refund eligibility status enum."""

    ELIGIBLE = "Eligible"
    PARTIALLY_ELIGIBLE = "Partially Eligible"
    INELIGIBLE = "Ineligible"


class ProductEligibilityInfo(TypedDict):
    """Information about product eligibility."""

    delivery_date: date
    price: float
    quantity: int = 1


@dataclass
class RefundEligibility:
    """Value object representing refund eligibility calculation result."""

    status: EligibilityStatus
    refund_amount: float
    details: List[Dict[str, Any]]  # Details about which products are eligible

    @classmethod
    def calculate_eligibility(
        cls,
        delivery_date: date,
        product_price: float,
        quantity: int = 1,
        days_threshold: int = 14,
    ) -> "RefundEligibility":
        """
        Calculate eligibility for a single product.

        Args:
            delivery_date: Date when product was delivered
            product_price: Price of the product
            quantity: Quantity of the product
            days_threshold: Number of days products are eligible for refund

        Returns:
            RefundEligibility object with status and refund amount
        """
        days_since_delivery = (datetime.utcnow().date() - delivery_date).days

        # If delivery date is in the future, treat as eligible
        if days_since_delivery < 0:
            eligible = True
        else:
            eligible = days_since_delivery <= days_threshold

        if eligible:
            refund_amount = product_price * quantity
            status = EligibilityStatus.ELIGIBLE
            details = [
                {
                    "eligible": True,
                    "reason": "Within refund window"
                    if days_since_delivery >= 0
                    else "Future delivery date",
                    "amount": refund_amount,
                }
            ]
        else:
            refund_amount = 0.0
            status = EligibilityStatus.INELIGIBLE
            details = [
                {
                    "eligible": False,
                    "reason": f"Delivery date exceeded {days_threshold}-day refund window",
                    "days_since_delivery": days_since_delivery,
                    "amount": 0.0,
                }
            ]

        return cls(status=status, refund_amount=refund_amount, details=details)

    @classmethod
    def calculate_eligibility_for_products(
        cls, products: List[ProductEligibilityInfo], days_threshold: int = 14
    ) -> "RefundEligibility":
        """
        Calculate eligibility for multiple products.

        Args:
            products: List of product eligibility info
            days_threshold: Number of days products are eligible for refund

        Returns:
            RefundEligibility object with aggregated status and total refund amount
        """
        if not products:
            return cls(
                status=EligibilityStatus.INELIGIBLE, refund_amount=0.0, details=[]
            )

        individual_results = []
        total_refund_amount = 0.0
        eligible_count = 0
        total_count = len(products)

        for product in products:
            result = cls.calculate_eligibility(
                delivery_date=product["delivery_date"],
                product_price=product["price"],
                quantity=product.get("quantity", 1),
                days_threshold=days_threshold,
            )

            individual_results.append(
                {"product_info": product, "eligibility_result": result}
            )

            if result.status == EligibilityStatus.ELIGIBLE:
                total_refund_amount += result.refund_amount
                eligible_count += 1

        # Determine overall status
        if eligible_count == total_count:
            status = EligibilityStatus.ELIGIBLE
        elif eligible_count == 0:
            status = EligibilityStatus.INELIGIBLE
        else:
            status = EligibilityStatus.PARTIALLY_ELIGIBLE

        return cls(
            status=status, refund_amount=total_refund_amount, details=individual_results
        )

    def __repr__(self):
        return f"<RefundEligibility status={self.status.value} amount=${self.refund_amount:.2f}>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "status": self.status.value,
            "refund_amount": self.refund_amount,
            "details": self.details,
        }
