from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.refund_case import RefundCase
from src.database.session import SessionLocal


class RefundCaseRepository:
    """Repository for refund cases."""

    def __init__(self):
        self.db = SessionLocal()

    def create(self, refund_case: RefundCase) -> RefundCase:
        """Create a new refund case."""
        self.db.add(refund_case)
        self.db.commit()
        self.db.refresh(refund_case)
        return refund_case

    def get_by_id(self, refund_id: str) -> Optional[RefundCase]:
        """Get refund case by ID."""
        return self.db.query(RefundCase).filter(RefundCase.id == refund_id).first()

    def get_by_customer(self, customer_id: str) -> List[RefundCase]:
        """Get all refund cases for a customer."""
        return (
            self.db.query(RefundCase)
            .filter(RefundCase.customer_id == customer_id)
            .all()
        )

    def get_by_support_case(self, support_case_id: str) -> List[RefundCase]:
        """Get all refund cases for a support case."""
        return (
            self.db.query(RefundCase)
            .filter(RefundCase.support_case_id == support_case_id)
            .all()
        )

    def get_by_status(self, status: str) -> List[RefundCase]:
        """Get all refund cases by status."""
        return self.db.query(RefundCase).filter(RefundCase.status == status).all()

    def get_all(self) -> List[RefundCase]:
        """Get all refund cases."""
        return self.db.query(RefundCase).all()

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
