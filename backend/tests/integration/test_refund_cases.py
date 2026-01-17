"""Integration tests for refund case creation workflow."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from src.infrastructure.database.database import Base
from src.domain.entities.support_case import SupportCase
from src.domain.entities.refund_case import RefundCase
from src.domain.repositories.refund_case_repository import (
    SQLAlchemyRefundCaseRepository,
)
from src.application.use_cases.create_refund_case import CreateRefundCase


class TestRefundCaseIntegration:
    """Integration tests for refund case workflow."""

    @pytest.fixture
    def session(self):
        """Create test database session."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_full_refund_case_creation_workflow(self, session):
        """Test complete refund case creation workflow."""
        # First create a support case
        support_case = SupportCase(
            case_id="123e4567-e89b-12d3-a456-426614174000",
            customer_id="223e4567-e89b-12d3-a456-426614174000",
            order_id="323e4567-e89b-12d3-a456-426614174000",
            title="Test Support Case",
            description="Test Description",
            status="open",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(support_case)
        session.commit()

        # Test repository
        repository = SQLAlchemyRefundCaseRepository(session)

        # Create refund case
        refund_case = RefundCase(
            refund_id="423e4567-e89b-12d3-a456-426614174000",
            support_case_id=support_case.case_id,
            status="pending",
            requested_amount=150.00,
            delivery_date=datetime.now(),
            refund_requested_at=datetime.now(),
        )

        repository.save(refund_case)

        # Test retrieval
        retrieved_case = repository.find_by_id(refund_case.refund_id)
        assert retrieved_case is not None
        assert retrieved_case.requested_amount == 150.00

    def test_create_refund_case_use_case_integration(self, session):
        """Test create refund case use case with repository integration."""
        # Create support case first
        support_case = SupportCase(
            case_id="123e4567-e89b-12d3-a456-426614174000",
            customer_id="223e4567-e89b-12d3-a456-426614174000",
            order_id="323e4567-e89b-12d3-a456-426614174000",
            title="Test Support Case",
            description="Test Description",
            status="open",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(support_case)
        session.commit()

        # Test use case
        repository = SQLAlchemyRefundCaseRepository(session)
        use_case = CreateRefundCase(repository)

        # This should fail initially since the use case doesn't exist
        result = use_case.execute(
            {
                "support_case_id": support_case.case_id,
                "items": [
                    {
                        "product_id": "523e4567-e89b-12d3-a456-426614174000",
                        "product_name": "Office Chair",
                        "requested_quantity": 1,
                        "original_unit_price": "150.00",
                    }
                ],
                "delivery_date": "2024-01-01T00:00:00",
            }
        )

        # This assertion should fail initially
        assert result["refund_id"] is not None
        assert result["requested_amount"] == "150.00"
