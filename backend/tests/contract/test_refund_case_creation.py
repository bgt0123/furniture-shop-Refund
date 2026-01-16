import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi.testclient import TestClient
from main import create_app
from uuid import uuid4


class TestRefundCaseCreationContract:
    """Contract test for refund case creation API."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)

    def test_create_refund_case_contract(self, client):
        """Test refund case creation contract."""
        # First create a support case
        customer_id = str(uuid4())
        support_case_response = client.post(
            "/api/v1/support/cases/",
            json={
                "customer_id": customer_id,
                "order_id": "order-123",
                "products": [{"id": "prod-1", "name": "Chair", "price": 99.99}],
                "issue_description": "Broken leg",
                "attachments": [],
            },
        )
        assert support_case_response.status_code == 200
        support_case_id = support_case_response.json()["id"]

        # Now create refund case
        response = client.post(
            f"/api/v1/support/cases/{support_case_id}/refunds",
            json={
                "customer_id": customer_id,
                "order_id": "order-123",
                "products": [
                    {"id": "prod-1", "name": "Chair", "price": 99.99, "quantity": 1}
                ],
                "reason": "Product arrived damaged",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response contract
        assert "id" in data
        assert data["support_case_id"] == support_case_id
        assert data["customer_id"] == customer_id
        assert data["order_id"] == "order-123"
        assert "products" in data
        assert data["products"][0]["id"] == "prod-1"
        assert data["status"] == "Pending"
        assert data["eligibility_status"] == "Eligible"
        assert "created_at" in data
        assert "total_refund_amount" in data

    def test_get_refund_case_contract(self, client):
        """Test get refund case contract."""
        # First create support case
        customer_id = str(uuid4())
        support_case_response = client.post(
            "/api/v1/support/cases/",
            json={
                "customer_id": customer_id,
                "order_id": "order-456",
                "products": [{"id": "prod-2", "name": "Table", "price": 199.99}],
                "issue_description": "Scratched surface",
                "attachments": [],
            },
        )
        assert support_case_response.status_code == 200
        support_case_id = support_case_response.json()["id"]

        # Create refund case
        refund_response = client.post(
            f"/api/v1/support/cases/{support_case_id}/refunds",
            json={
                "customer_id": customer_id,
                "order_id": "order-456",
                "products": [
                    {"id": "prod-2", "name": "Table", "price": 199.99, "quantity": 1}
                ],
                "reason": "Product has scratches",
            },
        )
        assert refund_response.status_code == 200
        refund_id = refund_response.json()["id"]

        # Then retrieve it
        response = client.get(f"/api/v1/refunds/cases/{refund_id}")
        assert response.status_code == 200

        data = response.json()
        # Verify contract
        assert data["id"] == refund_id
        assert data["support_case_id"] == support_case_id
        assert "customer_id" in data
        assert "order_id" in data
        assert "products" in data
        assert "total_refund_amount" in data
        assert "status" in data
        assert "eligibility_status" in data
        assert "created_at" in data

    def test_get_customer_refund_cases_contract(self, client):
        """Test get customer refund cases contract."""
        customer_id = str(uuid4())

        # Create support case
        support_case_response = client.post(
            "/api/v1/support/cases/",
            json={
                "customer_id": customer_id,
                "order_id": "order-789",
                "products": [{"id": "prod-3", "name": "Lamp", "price": 49.99}],
                "issue_description": "Bulb not working",
                "attachments": [],
            },
        )
        assert support_case_response.status_code == 200
        support_case_id = support_case_response.json()["id"]

        # Create refund case
        refund_response = client.post(
            f"/api/v1/support/cases/{support_case_id}/refunds",
            json={
                "customer_id": customer_id,
                "order_id": "order-789",
                "products": [
                    {"id": "prod-3", "name": "Lamp", "price": 49.99, "quantity": 1}
                ],
                "reason": "Product defective",
            },
        )
        assert refund_response.status_code == 200

        response = client.get(f"/api/v1/refunds/cases/customer/{customer_id}")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

        # Verify contract for items in list
        refund_data = data[0]
        assert "id" in refund_data
        assert refund_data["customer_id"] == customer_id
        assert "order_id" in refund_data
        assert "products" in refund_data
        assert "total_refund_amount" in refund_data
        assert "status" in refund_data
        assert "eligibility_status" in refund_data

    def test_validation_error_contract(self, client):
        """Test validation error contract."""
        # Send invalid data - missing required fields
        invalid_case_id = str(uuid4())
        response = client.post(
            f"/api/v1/support/cases/{invalid_case_id}/refunds",
            json={
                "customer_id": "invalid-uuid",  # Should be UUID
                "order_id": "order-123",
                "products": "not-a-list",  # Should be list
                "reason": "Test reason",
            },
        )

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_not_found_contract(self, client):
        """Test not found contract."""
        non_existent_id = str(uuid4())
        response = client.get(f"/api/v1/refunds/cases/{non_existent_id}")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_eligibility_check_contract(self, client):
        """Test eligibility check contract."""
        customer_id = str(uuid4())
        support_case_response = client.post(
            "/api/v1/support/cases/",
            json={
                "customer_id": customer_id,
                "order_id": "order-expired",
                "products": [
                    {
                        "id": "prod-old",
                        "name": "Old Product",
                        "price": 29.99,
                        "delivery_date": "2024-01-01T00:00:00Z",  # Old delivery date
                    }
                ],
                "issue_description": "Product issue",
                "attachments": [],
            },
        )
        assert support_case_response.status_code == 200
        support_case_id = support_case_response.json()["id"]

        # Create refund case for old product
        response = client.post(
            f"/api/v1/support/cases/{support_case_id}/refunds",
            json={
                "customer_id": customer_id,
                "order_id": "order-expired",
                "products": [
                    {
                        "id": "prod-old",
                        "name": "Old Product",
                        "price": 29.99,
                        "quantity": 1,
                        "delivery_date": "2024-01-01T00:00:00Z",
                    }
                ],
                "reason": "Product issue",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Should be ineligible due to old delivery date
        assert data["eligibility_status"] == "Ineligible"
