import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi.testclient import TestClient
from main import create_app
from uuid import uuid4


class TestSupportCaseCreationContract:
    """Contract test for support case creation API."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)

    def test_create_support_case_contract(self, client):
        """Test support case creation contract."""
        customer_id = str(uuid4())
        order_id = str(uuid4())

        response = client.post(
            "/api/v1/support/cases/",
            json={
                "customer_id": customer_id,
                "order_id": order_id,
                "products": [{"id": "prod-1", "name": "Chair"}],
                "issue_description": "Broken leg",
                "attachments": [],
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response contract
        assert "id" in data
        assert data["customer_id"] == customer_id
        assert data["order_id"] == order_id
        assert data["products"] == [{"id": "prod-1", "name": "Chair"}]
        assert data["issue_description"] == "Broken leg"
        assert data["status"] == "Open"
        assert "created_at" in data
        assert data["closed_at"] is None

    def test_get_support_case_contract(self, client):
        """Test get support case contract."""
        # First create a case
        customer_id = str(uuid4())
        response = client.post(
            "/api/v1/support/cases/",
            json={
                "customer_id": customer_id,
                "order_id": str(uuid4()),
                "products": [],
                "issue_description": "Test issue",
                "attachments": [],
            },
        )

        assert response.status_code == 200
        case_id = response.json()["id"]

        # Then retrieve it
        response = client.get(f"/api/v1/support/cases/{case_id}")
        assert response.status_code == 200

        data = response.json()
        # Verify contract
        assert data["id"] == case_id
        assert "customer_id" in data
        assert "order_id" in data
        assert "products" in data
        assert "issue_description" in data
        assert "status" in data
        assert "created_at" in data

    def test_get_customer_support_cases_contract(self, client):
        """Test get customer support cases contract."""
        customer_id = str(uuid4())

        # Create a case for this customer
        response = client.post(
            "/api/v1/support/cases/",
            json={
                "customer_id": customer_id,
                "order_id": str(uuid4()),
                "products": [],
                "issue_description": "First issue",
                "attachments": [],
            },
        )
        assert response.status_code == 200

        response = client.get(f"/api/v1/support/cases/customer/{customer_id}")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

        # Verify contract for items in list
        case_data = data[0]
        assert "id" in case_data
        assert case_data["customer_id"] == customer_id
        assert "order_id" in case_data
        assert "products" in case_data
        assert "issue_description" in case_data
        assert "status" in case_data

    def test_close_support_case_contract(self, client):
        """Test close support case contract."""
        # First create a case
        response = client.post(
            "/api/v1/support/cases/",
            json={
                "customer_id": str(uuid4()),
                "order_id": str(uuid4()),
                "products": [],
                "issue_description": "Test issue",
                "attachments": [],
            },
        )

        assert response.status_code == 200
        case_id = response.json()["id"]

        # Then close it
        response = client.patch(f"/api/v1/support/cases/{case_id}/close")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == case_id
        assert data["status"] == "Closed"
        assert data["closed_at"] is not None

    def test_validation_error_contract(self, client):
        """Test validation error contract."""
        # Send invalid data
        response = client.post(
            "/api/v1/support/cases/",
            json={
                "customer_id": "invalid-uuid",  # Should be UUID
                "order_id": "invalid-uuid",
                "products": "not-a-list",  # Should be list
                "issue_description": "Test issue",
            },
        )

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_not_found_contract(self, client):
        """Test not found contract."""
        non_existent_id = str(uuid4())
        response = client.get(f"/api/v1/support/cases/{non_existent_id}")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
