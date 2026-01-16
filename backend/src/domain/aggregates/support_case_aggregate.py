"""Support case aggregate."""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from ..entities.support_case import SupportCase
from ..entities.refund_case import RefundCase
from ..value_objects.case_status import CaseStatus


class SupportCaseAggregate:
    """Support case aggregate root."""

    def __init__(
        self, support_case: SupportCase, refund_cases: Optional[List[RefundCase]] = None
    ):
        self.support_case = support_case
        self.refund_cases = refund_cases or []

    @classmethod
    def create_new(
        cls,
        customer_id: str,
        order_id: str,
        title: str,
        description: Optional[str] = None,
    ) -> "SupportCaseAggregate":
        """Create a new support case aggregate."""
        support_case = SupportCase(
            case_id=str(uuid4()),
            customer_id=customer_id,
            order_id=order_id,
            title=title,
            description=description,
            status=CaseStatus.OPEN.value,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        return cls(support_case)

    def add_refund_case(
        self, requested_amount: float, delivery_date: datetime, product_ids: List[str]
    ) -> RefundCase:
        """Add a refund case to this support case."""
        refund_case = RefundCase(
            refund_id=str(uuid4()),
            support_case_id=self.support_case.case_id,
            status="pending",
            requested_amount=requested_amount,
            delivery_date=delivery_date,
            refund_requested_at=datetime.utcnow(),
        )
        self.refund_cases.append(refund_case)
        return refund_case

    def update_status(self, new_status: CaseStatus) -> bool:
        """Update support case status."""
        current_status = CaseStatus(self.support_case.status)

        if not current_status.can_transition_to(new_status):
            return False

        self.support_case.status = new_status.value
        self.support_case.updated_at = datetime.utcnow()

        if new_status == CaseStatus.CLOSED:
            self.support_case.closed_at = datetime.utcnow()

        return True

    def get_open_refunds(self) -> List[RefundCase]:
        """Get all open refund cases."""
        return [rc for rc in self.refund_cases if rc.status in ["pending", "approved"]]
