import pytest
import sys
import os

# Add the src directory to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from models.support_case import SupportCase, SupportCaseStatus
from models.refund_case import (
    RefundCase,
    RefundCaseStatus,
    EligibilityStatus,
)


def test_support_case_creation():
    """Test support case creation."""
    case = SupportCase(
        customer_id="test-customer-id",
        order_id="test-order-id",
        products=[{"product_id": "test-product-id", "quantity": 1}],
        issue_description="Test issue description",
        status=SupportCaseStatus.OPEN,
    )

    assert case.customer_id == "test-customer-id"
    assert case.order_id == "test-order-id"
    assert case.status == SupportCaseStatus.OPEN
    assert len(case.products) == 1
    assert case.issue_description == "Test issue description"


def test_support_case_close():
    """Test support case closing."""
    case = SupportCase(
        customer_id="test-customer-id",
        order_id="test-order-id",
        products=[{"product_id": "test-product-id", "quantity": 1}],
        issue_description="Test issue description",
        status=SupportCaseStatus.OPEN,
    )

    case.close()
    assert case.status == SupportCaseStatus.CLOSED
    assert case.closed_at is not None


def test_refund_case_creation():
    """Test refund case creation."""
    refund_case = RefundCase(
        support_case_id="test-support-case-id",
        customer_id="test-customer-id",
        order_id="test-order-id",
        products=[
            {
                "product_id": "test-product-id",
                "quantity": 1,
                "price": 100.0,
                "refund_amount": 100.0,
            }
        ],
        total_refund_amount=100.0,
        eligibility_status=EligibilityStatus.ELIGIBLE,
        status=RefundCaseStatus.PENDING,
    )

    assert refund_case.support_case_id == "test-support-case-id"
    assert refund_case.customer_id == "test-customer-id"
    assert refund_case.status == RefundCaseStatus.PENDING
    assert refund_case.total_refund_amount == 100.0


def test_refund_case_approval():
    """Test refund case approval."""
    refund_case = RefundCase(
        support_case_id="test-support-case-id",
        customer_id="test-customer-id",
        order_id="test-order-id",
        products=[
            {
                "product_id": "test-product-id",
                "quantity": 1,
                "price": 100.0,
                "refund_amount": 100.0,
            }
        ],
        total_refund_amount=100.0,
        eligibility_status=EligibilityStatus.ELIGIBLE,
        status=RefundCaseStatus.PENDING,
    )

    refund_case.approve("test-agent-id")
    assert refund_case.status == RefundCaseStatus.APPROVED
    assert refund_case.agent_id == "test-agent-id"
    assert refund_case.processed_at is not None
