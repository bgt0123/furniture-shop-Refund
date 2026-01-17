"""Contract tests for support cases endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from src.main import app


class TestSupportCasesEndpoints:
    """Contract tests for support cases API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_create_support_case_endpoint_contract(self, client):
        """Test that create support case endpoint contract is correct."""
        # This test should fail initially since the endpoint doesn't exist
        with patch(
            "src.api.endpoints.support_cases.CreateSupportCase"
        ) as mock_use_case:
            mock_use_case.return_value.execute.return_value = {
                "case_id": "123e4567-e89b-12d3-a456-426614174000",
                "customer_id": "123e4567-e89b-12d3-a456-426614174000",
                "order_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Test Case",
                "description": "Test Description",
                "status": "open",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }

            response = client.post(
                "/api/support-cases",
                json={
                    "customer_id": "123e4567-e89b-12d3-a456-426614174000",
                    "order_id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Test Case",
                    "description": "Test Description",
                },
            )

            # This should fail initially since the endpoint doesn't exist
            assert response.status_code == 201
            assert response.json()["case_id"] == "123e4567-e89b-12d3-a456-426614174000"

    def test_get_support_case_endpoint_contract(self, client):
        """Test that get support case endpoint contract is correct."""
        # This test should fail initially since the endpoint doesn't exist
        with patch("src.api.endpoints.support_cases.GetSupportCase") as mock_use_case:
            mock_use_case.return_value.execute.return_value = {
                "case_id": "123e4567-e89b-12d3-a456-426614174000",
                "customer_id": "123e4567-e89b-12d3-a456-426614174000",
                "order_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Test Case",
                "description": "Test Description",
                "status": "open",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }

            response = client.get(
                "/api/support-cases/123e4567-e89b-12d3-a456-426614174000"
            )

            # This should fail initially since the endpoint doesn't exist
            assert response.status_code == 200
            assert response.json()["case_id"] == "123e4567-e89b-12d3-a456-426614174000"

    def test_update_support_case_status_endpoint_contract(self, client):
        """Test that update support case status endpoint contract is correct."""
        # This test should fail initially since the endpoint doesn't exist
        with patch(
            "src.api.endpoints.support_cases.UpdateSupportCaseStatus"
        ) as mock_use_case:
            mock_use_case.return_value.execute.return_value = {
                "case_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "in_progress",
                "updated_at": "2024-01-01T00:00:00",
            }

            response = client.patch(
                "/api/support-cases/123e4567-e89b-12d3-a456-426614174000/status",
                json={"status": "in_progress"},
            )

            # This should fail initially since the endpoint doesn't exist
            assert response.status_code == 200
            assert response.json()["status"] == "in_progress"
