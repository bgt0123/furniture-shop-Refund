import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from uuid import uuid4
from services.support_case_service import SupportCaseService
from models.support_case import SupportCase


class TestSupportCaseCreationJourney:
    """Integration test for support case creation journey."""

    def test_create_and_retrieve_support_case(self):
        """Test the complete journey of creating and retrieving a support case."""
        service = SupportCaseService()

        # Create support case
        customer_id = uuid4()
        order_id = uuid4()
        products = [{"id": "prod-1", "name": "Chair", "price": 199.99}]
        issue_description = "Broken leg on arrival"

        # Create the support case
        support_case = service.create_support_case(
            customer_id=customer_id,
            order_id=order_id,
            products=products,
            issue_description=issue_description,
        )

        # Verify creation
        assert support_case is not None
        assert support_case.customer_id == str(customer_id)
        assert support_case.order_id == str(order_id)
        assert support_case.products == products
        assert support_case.issue_description == issue_description
        assert support_case.status.value == "Open"
        assert support_case.created_at is not None
        assert support_case.closed_at is None

        # Retrieve the same case by ID
        retrieved_case = service.get_support_case(support_case.id)
        assert retrieved_case is not None
        assert retrieved_case.id == support_case.id
        assert retrieved_case.customer_id == str(customer_id)

        # Retrieve customer's cases
        customer_cases = service.get_customer_support_cases(customer_id)
        assert len(customer_cases) == 1
        assert customer_cases[0].id == support_case.id

    def test_close_support_case_journey(self):
        """Test closing a support case."""
        service = SupportCaseService()

        # Create case
        customer_id = uuid4()
        support_case = service.create_support_case(
            customer_id=customer_id,
            order_id=uuid4(),
            products=[],
            issue_description="Test issue",
        )

        assert support_case.status.value == "Open"
        assert support_case.closed_at is None

        # Close the case
        closed_case = service.close_support_case(support_case.id)
        assert closed_case is not None
        assert closed_case.status.value == "Closed"
        assert closed_case.closed_at is not None

        # Try to get closed case
        retrieved_case = service.get_support_case(support_case.id)
        assert retrieved_case.status.value == "Closed"

    def test_add_attachment_to_case(self):
        """Test adding attachments to a support case."""
        service = SupportCaseService()

        # Create case
        support_case = service.create_support_case(
            customer_id=uuid4(),
            order_id=uuid4(),
            products=[],
            issue_description="Test issue",
        )

        assert len(support_case.attachments) == 0

        # Add attachment
        attachment = {
            "filename": "receipt.jpg",
            "type": "image",
            "url": "/uploads/receipt.jpg",
        }

        updated_case = service.add_attachment(support_case.id, attachment)
        assert updated_case is not None
        assert len(updated_case.attachments) == 1
        assert updated_case.attachments[0] == attachment
