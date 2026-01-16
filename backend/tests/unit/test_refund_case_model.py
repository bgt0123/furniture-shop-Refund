import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.refund_case import RefundCase, RefundCaseStatus, EligibilityStatus


class TestRefundCaseModel:
    """Test RefundCase model validation."""

    def test_refund_case_creation_with_attributes(self):
        """Test that RefundCase has correct attributes defined."""
        # Test that the RefundCase class exists and has expected columns
        assert hasattr(RefundCase, "id")
        assert hasattr(RefundCase, "support_case_id")
        assert hasattr(RefundCase, "customer_id")
        assert hasattr(RefundCase, "order_id")
        assert hasattr(RefundCase, "products")
        assert hasattr(RefundCase, "total_refund_amount")
        assert hasattr(RefundCase, "status")
        assert hasattr(RefundCase, "eligibility_status")
        assert hasattr(RefundCase, "created_at")
        assert hasattr(RefundCase, "processed_at")
        assert hasattr(RefundCase, "rejection_reason")
        assert hasattr(RefundCase, "agent_id")

    def test_refund_case_status_enum(self):
        """Test RefundCaseStatus enum values."""
        assert RefundCaseStatus.PENDING == "Pending"
        assert RefundCaseStatus.APPROVED == "Approved"
        assert RefundCaseStatus.REJECTED == "Rejected"
        assert RefundCaseStatus.COMPLETED == "Completed"

    def test_eligibility_status_enum(self):
        """Test EligibilityStatus enum values."""
        assert EligibilityStatus.ELIGIBLE == "Eligible"
        assert EligibilityStatus.PARTIALLY_ELIGIBLE == "Partially Eligible"
        assert EligibilityStatus.INELIGIBLE == "Ineligible"

    def test_refund_case_methods_exist(self):
        """Test that RefundCase methods exist."""
        # Test that expected methods exist
        assert hasattr(RefundCase, "approve")
        assert hasattr(RefundCase, "reject")
        assert hasattr(RefundCase, "complete")

    def test_model_table_name(self):
        """Test that RefundCase has correct table name."""
        assert RefundCase.__tablename__ == "refund_cases"

    def test_refund_case_repr_method(self):
        """Test that __repr__ method returns expected format."""
        # Create a mock refund case
        refund_case = RefundCase()
        refund_case.id = "test-refund-id"
        refund_case.status = RefundCaseStatus.PENDING
        refund_case.total_refund_amount = 99.99

        # Test repr format
        repr_str = repr(refund_case)
        assert "test-refund-id" in repr_str
        assert "Pending" in repr_str
        assert "99.99" in repr_str

    def test_approve_method(self):
        """Test approve method functionality."""
        refund_case = RefundCase()
        refund_case.status = RefundCaseStatus.PENDING
        import uuid

        agent_id = uuid.uuid4()

        refund_case.approve(agent_id)

        assert refund_case.status == RefundCaseStatus.APPROVED
        assert refund_case.agent_id == str(agent_id)
        assert refund_case.processed_at is not None

    def test_reject_method(self):
        """Test reject method functionality."""
        refund_case = RefundCase()
        refund_case.status = RefundCaseStatus.PENDING
        import uuid

        agent_id = uuid.uuid4()
        reason = "Insufficient documentation"

        refund_case.reject(agent_id, reason)

        assert refund_case.status == RefundCaseStatus.REJECTED
        assert refund_case.agent_id == str(agent_id)
        assert refund_case.rejection_reason == reason
        assert refund_case.processed_at is not None

    def test_complete_method(self):
        """Test complete method functionality."""
        # Test completion from APPROVED status
        refund_case = RefundCase()
        refund_case.status = RefundCaseStatus.APPROVED
        refund_case.complete()
        assert refund_case.status == RefundCaseStatus.COMPLETED

        # Test completion from REJECTED status
        refund_case.status = RefundCaseStatus.REJECTED
        refund_case.complete()
        assert refund_case.status == RefundCaseStatus.COMPLETED

        # Test should not complete from PENDING status
        refund_case.status = RefundCaseStatus.PENDING
        refund_case.complete()
        assert refund_case.status == RefundCaseStatus.PENDING  # Should not change
