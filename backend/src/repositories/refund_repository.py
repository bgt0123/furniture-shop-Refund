"""Repository for refund cases."""

from typing import List, Optional
from database.session import SessionLocal
from models.refund_case import RefundCase


class RefundCaseRepository:
    """Repository for refund cases."""

    def __init__(self, db_session):
        self.db = db_session

    def create(self, refund_case: RefundCase) -> RefundCase:
        """Create a new refund case."""
        self.db.add(refund_case)
        self.db.commit()
        self.db.refresh(refund_case)
        return refund_case

    def get_by_id(self, refund_id: str) -> Optional[RefundCase]:
        """Get refund case by ID."""
        return self.db.query(RefundCase).filter(RefundCase.id == refund_id).first()

    def get_by_customer(
        self, customer_id: str, limit: int = 50, offset: int = 0
    ) -> List[RefundCase]:
        """Get all refund cases for a customer."""
        return (
            self.db.query(RefundCase)
            .filter(RefundCase.customer_id == customer_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_support_case(
        self, support_case_id: str, limit: int = 50, offset: int = 0
    ) -> List[RefundCase]:
        """Get all refund cases for a support case."""
        return (
            self.db.query(RefundCase)
            .filter(RefundCase.support_case_id == support_case_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self, status: str, limit: int = 50, offset: int = 0
    ) -> List[RefundCase]:
        """Get refund cases by status."""
        return (
            self.db.query(RefundCase)
            .filter(RefundCase.status == status)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_customer(
        self, customer_id: str, limit: int = 50, offset: int = 0
    ) -> List[RefundCase]:
        """Get refund cases for a customer with pagination."""
        return (
            self.db.query(RefundCase)
            .filter(RefundCase.customer_id == customer_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_all(self, limit: int = 50, offset: int = 0) -> List[RefundCase]:
        """Get all refund cases with pagination."""
        return self.db.query(RefundCase).offset(offset).limit(limit).all()

    def count_by_status(self, status: str) -> int:
        """Count refund cases by status."""
        return self.db.query(RefundCase).filter(RefundCase.status == status).count()

    def get_pending_refunds_for_support_case(
        self, support_case_id: str
    ) -> List[RefundCase]:
        """Get pending refund cases for a support case."""
        return (
            self.db.query(RefundCase)
            .filter(
                RefundCase.support_case_id == support_case_id,
                RefundCase.status == "Pending",
            )
            .all()
        )

    def update(self, refund_case: RefundCase) -> RefundCase:
        """Update refund case."""
        self.db.commit()
        self.db.refresh(refund_case)
        return refund_case

    def delete(self, refund_id: str) -> bool:
        """Delete refund case."""
        refund_case = self.get_by_id(refund_id)
        if refund_case:
            self.db.delete(refund_case)
            self.db.commit()
            return True
        return False
