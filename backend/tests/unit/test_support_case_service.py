import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unittest.mock import Mock, patch
from uuid import uuid4
from src.services.support_case_service import SupportCaseService
from src.models.support_case import SupportCase, SupportCaseStatus


class TestSupportCaseService:
    """Test SupportCaseService functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.mock_repository = Mock()
        self.service = SupportCaseService(repository=self.mock_repository)

    def test_create_support_case(self):
        """Test creating a support case via service."""
        customer_id = uuid4()
        order_id = uuid4()
        products = [{"id": "prod-1", "name": "Chair"}]
        issue_description = "Broken leg"

        mock_case = Mock()
        self.mock_repository.create.return_value = mock_case

        result = self.service.create_support_case(
            customer_id=customer_id,
            order_id=order_id,
            products=products,
            issue_description=issue_description,
        )

        assert result == mock_case
        self.mock_repository.create.assert_called_once()
        # Verify SupportCase was created with correct parameters
        call_args = self.mock_repository.create.call_args[0][0]
        assert call_args.customer_id == str(customer_id)
        assert call_args.order_id == str(order_id)
        assert call_args.products == products
        assert call_args.issue_description == issue_description
        assert call_args.status == SupportCaseStatus.OPEN

    def test_get_support_case(self):
        """Test getting a support case by ID."""
        case_id = uuid4()
        mock_case = Mock()
        self.mock_repository.get_by_id.return_value = mock_case

        result = self.service.get_support_case(case_id)

        assert result == mock_case
        self.mock_repository.get_by_id.assert_called_once_with(str(case_id))

    def test_get_customer_support_cases(self):
        """Test getting all support cases for a customer."""
        customer_id = uuid4()
        mock_cases = [Mock(), Mock()]
        self.mock_repository.get_by_customer.return_value = mock_cases

        result = self.service.get_customer_support_cases(customer_id)

        assert result == mock_cases
        self.mock_repository.get_by_customer.assert_called_once_with(str(customer_id))

    def test_close_support_case_success(self):
        """Test successfully closing a support case."""
        case_id = uuid4()
        mock_case = Mock()
        mock_case.can_close.return_value = True
        self.mock_repository.get_by_id.return_value = mock_case

        result = self.service.close_support_case(case_id)

        assert result == mock_case
        self.mock_repository.get_by_id.assert_called_once_with(str(case_id))
        mock_case.can_close.assert_called_once()
        mock_case.close.assert_called_once()
        self.mock_repository.update.assert_called_once_with(mock_case)

    def test_close_support_case_failure(self):
        """Test failing to close a support case."""
        case_id = uuid4()
        mock_case = Mock()
        mock_case.can_close.return_value = False
        self.mock_repository.get_by_id.return_value = mock_case

        result = self.service.close_support_case(case_id)

        assert result is None
        self.mock_repository.get_by_id.assert_called_once_with(str(case_id))
        mock_case.can_close.assert_called_once()
        mock_case.close.assert_not_called()
        self.mock_repository.update.assert_not_called()

    def test_close_nonexistent_case(self):
        """Test closing a non-existent support case."""
        case_id = uuid4()
        self.mock_repository.get_by_id.return_value = None

        result = self.service.close_support_case(case_id)

        assert result is None
        self.mock_repository.get_by_id.assert_called_once_with(str(case_id))
        self.mock_repository.update.assert_not_called()

    def test_add_attachment_success(self):
        """Test adding attachment to support case."""
        case_id = uuid4()
        mock_case = Mock()
        self.mock_repository.get_by_id.return_value = mock_case
        attachment = {"filename": "image.jpg", "type": "image"}

        result = self.service.add_attachment(case_id, attachment)

        assert result == mock_case
        self.mock_repository.get_by_id.assert_called_once_with(str(case_id))
        mock_case.add_attachment.assert_called_once_with(attachment)
        self.mock_repository.update.assert_called_once_with(mock_case)

    def test_add_attachment_failure(self):
        """Test adding attachment to non-existent support case."""
        case_id = uuid4()
        self.mock_repository.get_by_id.return_value = None
        attachment = {"filename": "image.jpg", "type": "image"}

        result = self.service.add_attachment(case_id, attachment)

        assert result is None
        self.mock_repository.get_by_id.assert_called_once_with(str(case_id))
        self.mock_repository.update.assert_not_called()
