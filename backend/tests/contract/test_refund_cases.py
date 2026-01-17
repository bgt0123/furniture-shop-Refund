"""Contract tests for refund cases endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from src.main import app


class TestRefundCasesEndpoints:
    """Contract tests for refund cases API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_create_refund_case_endpoint_contract(self, client):
        """Test that create refund case endpoint contract is correct."""
        # This test should fail initially since the endpoint doesn't exist
        with patch("src.api.endpoints.refund_cases.CreateRefundCase") as mock_use_case:
            mock_use_case.return_value.execute.return_value = {
                "refund_id": "223e4567-e89b-12d3-a456-426614174000",
                "support_case_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "pending",
                "requested_amount": "150.00",
                "delivery_date": "2024-01-01T00:00:00",
                "refund_requested_at": "2024-01-01T00:00:00",
            }

            response = client.post(
                "/api/refund-cases",
                json={
                    "support_case_id": "123e4567-e89b-12d3-a456-426614174000",
                    "items": [
                        {
                            "product_id": "323e4567-e89b-12d3-a456-426614174000",
                            "product_name": "Office Chair",
                            "requested_quantity": 1,
                            "original_unit_price": "150.00",
                        }
                    ],
                    "delivery_date": "2024-01-01T00:00:00",
                },
            )

            # This should fail initially since the endpoint doesn't exist
            assert response.status_code == 201
            assert (
                response.json()["refund_id"] == "223e4567-e89b-12d3-a456-426614174000"
            )

    def test_get_refund_case_endpoint_contract(self, client):
        """Test that get refund case endpoint contract is correct."""
        # This test should fail initially since the endpoint doesn't exist
        with patch("src.api.endpoints.refund_cases.GetRefundCase") as mock_use_case:
            mock_use_case.return_value.execute.return_value = {
                "refund_id": "223e4567-e89b-12d3-a456-426614174000",
                "support_case_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "pending",
                "requested_amount": "150.00",
                "approved_amount": None,
                "delivery_date": "2024-01-01T00:00:00",
                "refund_requested_at": "2024-01-01T00:00:00",
                "items": [
                    {
                        "product_id": "323e4567-e89b-12d3-a456-426614174000",
                        "product_name": "Office Chair",
                        "requested_quantity": 1,
                        "original_unit_price": "150.00",
                        "total_refund_amount": "150.00",
                    }
                ],
            }

            response = client.get(
                "/api/refund-cases/223e4567-e89b-12d3-a456-426614174000"
            )

            # This should fail initially since the endpoint doesn't exist
            assert response.status_code == 200
            assert (
                response.json()["refund_id"] == "223e4567-e89b-12d3-a456-426614174000"
            )

    def test_update_refund_case_endpoint_contract(self, client):
        """Test that update refund case endpoint contract is correct."""
        # This test should fail initially since the endpoint doesn't exist
        with patch("src.api.endpoints.refund_cases.UpdateRefundCase") as mock_use_case:
            mock_use_case.return_value.execute.return_value = {
                "refund_id": "223e4567-e89b-12d3-a456-426614174000",
                "status": "approved",
                "approved_amount": "150.00",
                "refund_approved_at": "2024-01-01T00:00:00",
            }

            response = client.patch(
                "/api/refund-cases/223e4567-e89b-12d3-a456-426614174000",
                json={"status": "approved", "approved_amount": "150.00"},
            )

            # This should fail initially since the endpoint doesn't exist
            assert response.status_code == 200
            assert response.json()["status"] == "approved"
