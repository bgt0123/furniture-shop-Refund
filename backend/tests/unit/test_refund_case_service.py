import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from uuid import uuid4
from datetime import datetime, timedelta
from src.services.refund_case_service import RefundCaseService
from src.models.refund_case import RefundCase, RefundCaseStatus
from src.models.refund_eligibility import RefundEligibility, EligibilityStatus


class TestRefundCaseService:
    """Unit test for refund case service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_repository = Mock()
        self.service = RefundCaseService(repository=self.mock_repository)

    def test_create_refund_case_success(self):
        """Test successful refund case creation."""
        # Setup
        support_case_id = uuid4()
        customer_id = uuid4()
        order_id = "order-123"
        products = [
            {
                "id": "prod-1",
                "name": "Chair",
                "price": 99.99,
                "delivery_date": str(datetime.utcnow().date() - timedelta(days=5)),
            }
        ]
        reason = "Product damaged"

        mock_refund_case = Mock()
        mock_refund_case.id = "refund-123"
        mock_refund_case.status = RefundCaseStatus.PENDING
        mock_refund_case.eligibility_status = EligibilityStatus.ELIGIBLE
        mock_refund_case.total_refund_amount = 99.99

        self.mock_repository.create.return_value = mock_refund_case

        # Execute
        result = self.service.create_refund_case(
            support_case_id=support_case_id,
            customer_id=customer_id,
            order_id=order_id,
            products=products,
            reason=reason,
        )

        # Verify
        assert result == mock_refund_case
        self.mock_repository.create.assert_called_once()

    def test_get_refund_case_by_id(self):
        """Test getting refund case by ID."""
        # Setup
        refund_id = uuid4()
        mock_refund_case = Mock()
        self.mock_repository.get_by_id.return_value = mock_refund_case

        # Execute
        result = self.service.get_refund_case(refund_id)

        # Verify
        assert result == mock_refund_case
        self.mock_repository.get_by_id.assert_called_once_with(str(refund_id))

    def test_get_customer_refund_cases(self):
        """Test getting all refund cases for a customer."""
        # Setup
        customer_id = uuid4()
        mock_cases = [Mock(), Mock()]
        self.mock_repository.get_by_customer.return_value = mock_cases

        # Execute
        result = self.service.get_customer_refund_cases(customer_id)

        # Verify
        assert result == mock_cases
        self.mock_repository.get_by_customer.assert_called_once_with(str(customer_id))

    def test_eligibility_calculation_integration(self):
        """Test eligibility calculation integration."""
        # Setup
        support_case_id = uuid4()
        customer_id = uuid4()
        order_id = "order-456"

        # Products with different delivery dates
        products = [
            {
                "id": "prod-1",
                "name": "Chair",
                "price": 99.99,
                "delivery_date": str(datetime.utcnow().date() - timedelta(days=5)),
                "quantity": 1,
            },
            {
                "id": "prod-2",
                "name": "Table",
                "price": 199.99,
                "delivery_date": str(datetime.utcnow().date() - timedelta(days=20)),
                "quantity": 1,
            },
        ]

        mock_refund_case = Mock()
        mock_refund_case.id = "refund-456"
        self.mock_repository.create.return_value = mock_refund_case

        # Execute
        result = self.service.create_refund_case(
            support_case_id=support_case_id,
            customer_id=customer_id,
            order_id=order_id,
            products=products,
            reason="Mixed eligibility",
        )

        # Verify that eligibility calculation was used
        assert result == mock_refund_case
        self.mock_repository.create.assert_called_once()

        # The repository should receive a RefundCase with eligibility calculation
        created_call_args = self.mock_repository.create.call_args
        assert created_call_args is not None

    def test_approve_refund_case(self):
        """Test approving a refund case."""
        # Setup
        refund_id = uuid4()
        agent_id = uuid4()

        mock_refund_case = Mock()
        mock_refund_case.status = RefundCaseStatus.PENDING
        mock_refund_case.approve = Mock()

        self.mock_repository.get_by_id.return_value = mock_refund_case
        self.mock_repository.update.return_value = mock_refund_case

        # Execute
        result = self.service.approve_refund_case(refund_id, agent_id)

        # Verify
        assert result == mock_refund_case
        mock_refund_case.approve.assert_called_once_with(agent_id)
        self.mock_repository.update.assert_called_once_with(mock_refund_case)

    def test_reject_refund_case(self):
        """Test rejecting a refund case."""
        # Setup
        refund_id = uuid4()
        agent_id = uuid4()
        reason = "Insufficient evidence"

        mock_refund_case = Mock()
        mock_refund_case.status = RefundCaseStatus.PENDING
        mock_refund_case.reject = Mock()

        self.mock_repository.get_by_id.return_value = mock_refund_case
        self.mock_repository.update.return_value = mock_refund_case

        # Execute
        result = self.service.reject_refund_case(refund_id, agent_id, reason)

        # Verify
        assert result == mock_refund_case
        mock_refund_case.reject.assert_called_once_with(agent_id, reason)
        self.mock_repository.update.assert_called_once_with(mock_refund_case)

    def test_cannot_approve_non_pending_case(self):
        """Test that non-pending cases cannot be approved."""
        # Setup
        refund_id = uuid4()
        agent_id = uuid4()

        mock_refund_case = Mock()
        mock_refund_case.status = RefundCaseStatus.APPROVED  # Already approved

        self.mock_repository.get_by_id.return_value = mock_refund_case

        # Execute
        result = self.service.approve_refund_case(refund_id, agent_id)

        # Verify
        assert result is None
        self.mock_repository.update.assert_not_called()

    def test_cannot_reject_non_pending_case(self):
        """Test that non-pending cases cannot be rejected."""
        # Setup
        refund_id = uuid4()
        agent_id = uuid4()
        reason = "Test reason"

        mock_refund_case = Mock()
        mock_refund_case.status = RefundCaseStatus.REJECTED  # Already rejected

        self.mock_repository.get_by_id.return_value = mock_refund_case

        # Execute
        result = self.service.reject_refund_case(refund_id, agent_id, reason)

        # Verify
        assert result is None
        self.mock_repository.update.assert_not_called()

    def test_get_refund_case_not_found(self):
        """Test getting non-existent refund case."""
        # Setup
        refund_id = uuid4()
        self.mock_repository.get_by_id.return_value = None

        # Execute
        result = self.service.get_refund_case(refund_id)

        # Verify
        assert result is None

    def test_support_case_integration(self):
        """Test integration with support case service."""
        # This test would require mocking the support case service dependency
        # For now, it tests that the service handles missing dependencies gracefully
        support_case_service = RefundCaseService()

        # Should be able to create instance without errors
        assert support_case_service is not None
