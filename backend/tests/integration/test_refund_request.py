import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from uuid import uuid4
from datetime import datetime, timedelta
from src.services.refund_case_service import RefundCaseService
from src.services.support_case_service import SupportCaseService
from src.models.refund_case import RefundCase, RefundCaseStatus, EligibilityStatus


class TestRefundRequestJourney:
    """Integration test for refund request journey."""

    def test_create_refund_case_from_support_case(self):
        """Test creating a refund case from a support case."""
        support_service = SupportCaseService()
        refund_service = RefundCaseService()

        # First create a support case
        customer_id = uuid4()
        order_id = str(uuid4())
        products = [
            {
                "id": "prod-1",
                "name": "Chair",
                "price": 199.99,
                "delivery_date": str(datetime.utcnow().date()),
            }
        ]

        support_case = support_service.create_support_case(
            customer_id=customer_id,
            order_id=order_id,
            products=products,
            issue_description="Product damaged",
        )

        # Create refund case
        refund_case = refund_service.create_refund_case(
            support_case_id=support_case.id,
            customer_id=customer_id,
            order_id=order_id,
            products=products,
            reason="Product arrived with broken leg",
        )

        # Verify refund case creation
        assert refund_case is not None
        assert refund_case.support_case_id == support_case.id
        assert refund_case.customer_id == str(customer_id)
        assert refund_case.order_id == order_id
        assert refund_case.products == products
        assert refund_case.status == RefundCaseStatus.PENDING
        assert refund_case.eligibility_status == EligibilityStatus.ELIGIBLE
        assert refund_case.created_at is not None
        assert refund_case.total_refund_amount == 199.99

        # Verify linkage to support case
        retrieved_refund = refund_service.get_refund_case(refund_case.id)
        assert retrieved_refund.support_case_id == support_case.id

    def test_refund_eligibility_check(self):
        """Test refund eligibility calculation."""
        support_service = SupportCaseService()
        refund_service = RefundCaseService()

        # Create support case with recently delivered product
        customer_id = uuid4()
        recent_delivery = datetime.utcnow().date() - timedelta(days=5)
        products = [
            {
                "id": "prod-2",
                "name": "Table",
                "price": 499.99,
                "delivery_date": str(recent_delivery),
            }
        ]

        support_case = support_service.create_support_case(
            customer_id=customer_id,
            order_id=str(uuid4()),
            products=products,
            issue_description="Scratched surface",
        )

        # Create refund case - should be eligible (within 14 days)
        refund_case = refund_service.create_refund_case(
            support_case_id=support_case.id,
            customer_id=customer_id,
            order_id=support_case.order_id,
            products=products,
            reason="Product has scratches",
        )

        assert refund_case.eligibility_status == EligibilityStatus.ELIGIBLE

    def test_refund_ineligibility_due_to_time(self):
        """Test refund ineligibility due to expired time window."""
        support_service = SupportCaseService()
        refund_service = RefundCaseService()

        # Create support case with old delivery
        customer_id = uuid4()
        old_delivery = datetime.utcnow().date() - timedelta(
            days=20
        )  # Beyond 14-day window
        products = [
            {
                "id": "prod-3",
                "name": "Lamp",
                "price": 89.99,
                "delivery_date": str(old_delivery),
            }
        ]

        support_case = support_service.create_support_case(
            customer_id=customer_id,
            order_id=str(uuid4()),
            products=products,
            issue_description="Bulb broken",
        )

        # Create refund case - should be ineligible
        refund_case = refund_service.create_refund_case(
            support_case_id=support_case.id,
            customer_id=customer_id,
            order_id=support_case.order_id,
            products=products,
            reason="Product defective",
        )

        assert refund_case.eligibility_status == EligibilityStatus.INELIGIBLE

    def test_get_customer_refund_cases_journey(self):
        """Test retrieving all refund cases for a customer."""
        support_service = SupportCaseService()
        refund_service = RefundCaseService()

        customer_id = uuid4()

        # Create multiple support cases
        support_case_1 = support_service.create_support_case(
            customer_id=customer_id,
            order_id=str(uuid4()),
            products=[{"id": "prod-1", "name": "Chair", "price": 199.99}],
            issue_description="Issue 1",
        )

        support_case_2 = support_service.create_support_case(
            customer_id=customer_id,
            order_id=str(uuid4()),
            products=[{"id": "prod-2", "name": "Table", "price": 499.99}],
            issue_description="Issue 2",
        )

        # Create refund cases
        refund_case_1 = refund_service.create_refund_case(
            support_case_id=support_case_1.id,
            customer_id=customer_id,
            order_id=support_case_1.order_id,
            products=support_case_1.products,
            reason="Reason 1",
        )

        refund_case_2 = refund_service.create_refund_case(
            support_case_id=support_case_2.id,
            customer_id=customer_id,
            order_id=support_case_2.order_id,
            products=support_case_2.products,
            reason="Reason 2",
        )

        # Retrieve customer's refund cases
        customer_refunds = refund_service.get_customer_refund_cases(customer_id)
        assert len(customer_refunds) == 2

        # Verify both cases are present
        refund_ids = [refund.id for refund in customer_refunds]
        assert refund_case_1.id in refund_ids
        assert refund_case_2.id in refund_ids

    def test_refund_amount_calculation(self):
        """Test refund amount calculation for multiple products."""
        support_service = SupportCaseService()
        refund_service = RefundCaseService()

        customer_id = uuid4()
        products = [
            {"id": "prod-1", "name": "Chair", "price": 199.99, "quantity": 1},
            {"id": "prod-2", "name": "Table", "price": 499.99, "quantity": 1},
        ]

        support_case = support_service.create_support_case(
            customer_id=customer_id,
            order_id=str(uuid4()),
            products=products,
            issue_description="Multiple issues",
        )

        # Request refund for all products
        refund_case = refund_service.create_refund_case(
            support_case_id=support_case.id,
            customer_id=customer_id,
            order_id=support_case.order_id,
            products=products,
            reason="Multiple defective products",
        )

        expected_amount = 199.99 + 499.99
        assert refund_case.total_refund_amount == expected_amount

    def test_partial_eligibility_scenario(self):
        """Test partial eligibility when some products are outside refund window."""
        support_service = SupportCaseService()
        refund_service = RefundCaseService()

        customer_id = uuid4()
        recent_delivery = datetime.utcnow().date() - timedelta(days=5)
        old_delivery = datetime.utcnow().date() - timedelta(days=20)

        products = [
            {
                "id": "prod-recent",
                "name": "Chair",
                "price": 199.99,
                "delivery_date": str(recent_delivery),
            },
            {
                "id": "prod-old",
                "name": "Table",
                "price": 499.99,
                "delivery_date": str(old_delivery),
            },
        ]

        support_case = support_service.create_support_case(
            customer_id=customer_id,
            order_id=str(uuid4()),
            products=products,
            issue_description="Mixed eligibility",
        )

        # Create refund case - should be partially eligible
        refund_case = refund_service.create_refund_case(
            support_case_id=support_case.id,
            customer_id=customer_id,
            order_id=support_case.order_id,
            products=products,
            reason="Some products eligible, some not",
        )

        assert refund_case.eligibility_status == EligibilityStatus.PARTIALLY_ELIGIBLE
        # Only the recent product should be refunded
        assert refund_case.total_refund_amount == 199.99
