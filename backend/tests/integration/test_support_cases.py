"""Integration tests for support case creation workflow."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database.database import Base
from src.domain.entities.customer import Customer
from src.domain.entities.support_case import SupportCase
from src.domain.repositories.support_case_repository import (
    SQLAlchemySupportCaseRepository,
)
from src.application.use_cases.create_support_case import CreateSupportCase


class TestSupportCaseIntegration:
    """Integration tests for support case workflow."""

    @pytest.fixture
    def session(self):
        """Create test database session."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_full_support_case_creation_workflow(self, session):
        """Test complete support case creation workflow."""
        # First create a customer
        customer = Customer(
            customer_id="123e4567-e89b-12d3-a456-426614174000",
            email="customer@example.com",
            first_name="John",
            last_name="Doe",
            created_at="2024-01-01T00:00:00",
        )
        session.add(customer)
        session.commit()

        # Test repository
        repository = SQLAlchemySupportCaseRepository(session)

        # Create support case
        support_case = SupportCase(
            case_id="223e4567-e89b-12d3-a456-426614174000",
            customer_id=customer.customer_id,
            order_id="323e4567-e89b-12d3-a456-426614174000",
            title="Test Support Case",
            description="Test Description",
            status="open",
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00",
        )

        repository.save(support_case)

        # Test retrieval
        retrieved_case = repository.find_by_id(support_case.case_id)
        assert retrieved_case is not None
        assert retrieved_case.title == "Test Support Case"

    def test_create_support_case_use_case_integration(self, session):
        """Test create support case use case with repository integration."""
        # Create customer first
        customer = Customer(
            customer_id="123e4567-e89b-12d3-a456-426614174000",
            email="customer@example.com",
            first_name="John",
            last_name="Doe",
            created_at="2024-01-01T00:00:00",
        )
        session.add(customer)
        session.commit()

        # Test use case
        repository = SQLAlchemySupportCaseRepository(session)
        use_case = CreateSupportCase(repository)

        # This should fail initially since the use case doesn't exist
        result = use_case.execute(
            {
                "customer_id": customer.customer_id,
                "order_id": "323e4567-e89b-12d3-a456-426614174000",
                "title": "Test Case",
                "description": "Test Description",
            }
        )

        # This assertion should fail initially
        assert result["case_id"] is not None
        assert result["title"] == "Test Case"
