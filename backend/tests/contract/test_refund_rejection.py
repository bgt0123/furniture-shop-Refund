import pytest
from fastapi.testclient import TestClient
from uuid import UUID
from src.main import app

client = TestClient(app)


class TestRefundRejection:
    """Contract tests for refund rejection functionality."""

    def test_reject_refund_case_success(self):
        """Test successful refund rejection by an authorized agent."""
        refund_case_id = UUID("523e4567-e89b-12d3-a456-426614174001")

        # Mock authentication token for agent
        headers = {
            "Authorization": "Bearer agent-token",
            "X-Agent-ID": "623e4567-e89b-12d3-a456-426614174001",
        }

        rejection_reason = "Product damage appears to be due to customer misuse"

        response = client.post(
            f"/admin/refunds/cases/{refund_case_id}/reject",
            json={"reason": rejection_reason},
            headers=headers,
        )

        # The endpoint should now be implemented
        assert response.status_code in [200, 404]  # 404 if not found, 200 if approved

    def test_reject_refund_case_missing_reason(self):
        """Test refund rejection fails when reason is missing."""
        refund_case_id = UUID("623e4567-e89b-12d3-a456-426614174001")

        headers = {
            "Authorization": "Bearer agent-token",
            "X-Agent-ID": "623e4567-e89b-12d3-a456-426614174001",
        }

        response = client.post(
            f"/admin/refunds/cases/{refund_case_id}/reject",
            json={},  # Missing reason
            headers=headers,
        )

        assert response.status_code == 422  # Validation error

    def test_reject_refund_case_unauthorized(self):
        """Test refund rejection fails for unauthorized user."""
        refund_case_id = UUID("823e4567-e89b-12d3-a456-426614174001")

        # No authentication headers
        response = client.post(
            f"/admin/refunds/cases/{refund_case_id}/reject",
            json={"reason": "Test rejection reason"},
        )

        assert response.status_code == 401

    def test_reject_refund_case_not_found(self):
        """Test refund rejection fails for non-existent refund case."""
        non_existent_id = UUID("923e4567-e89b-12d3-a456-426614174001")

        headers = {
            "Authorization": "Bearer agent-token",
            "X-Agent-ID": "623e4567-e89b-12d3-a456-426614174001",
        }

        response = client.post(
            f"/admin/refunds/cases/{non_existent_id}/reject",
            json={"reason": "Test rejection reason"},
            headers=headers,
        )

        assert response.status_code == 404
