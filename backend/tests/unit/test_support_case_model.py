import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import datetime
from src.models.support_case import SupportCase, SupportCaseStatus


class TestSupportCaseModel:
    """Test SupportCase model validation."""

    def test_support_case_creation_with_attributes(self):
        """Test that SupportCase has correct attributes defined."""
        # Test that the SupportCase class exists and has expected columns
        assert hasattr(SupportCase, "id")
        assert hasattr(SupportCase, "customer_id")
        assert hasattr(SupportCase, "order_id")
        assert hasattr(SupportCase, "products")
        assert hasattr(SupportCase, "issue_description")
        assert hasattr(SupportCase, "status")
        assert hasattr(SupportCase, "created_at")
        assert hasattr(SupportCase, "closed_at")
        assert hasattr(SupportCase, "attachments")

    def test_support_case_status_enum(self):
        """Test SupportCaseStatus enum values."""
        assert SupportCaseStatus.OPEN == "Open"
        assert SupportCaseStatus.CLOSED == "Closed"

    def test_support_case_methods_exist(self):
        """Test that SupportCase methods exist."""
        # Test that expected methods exist
        assert hasattr(SupportCase, "close")
        assert hasattr(SupportCase, "can_close")
        assert hasattr(SupportCase, "add_attachment")

    def test_model_table_name(self):
        """Test that SupportCase has correct table name."""
        assert SupportCase.__tablename__ == "support_cases"
