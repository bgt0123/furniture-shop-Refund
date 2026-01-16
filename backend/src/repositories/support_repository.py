from typing import List, Optional
from sqlalchemy.orm import Session
from models.support_case import SupportCase
from database.session import SessionLocal


class SupportCaseRepository:
    """Repository for support cases."""

    def __init__(self):
        self.db = SessionLocal()

    def create(self, support_case: SupportCase) -> SupportCase:
        """Create a new support case."""
        self.db.add(support_case)
        self.db.commit()
        self.db.refresh(support_case)
        return support_case

    def get_by_id(self, case_id: str) -> Optional[SupportCase]:
        """Get support case by ID."""
        return self.db.query(SupportCase).filter(SupportCase.id == case_id).first()

    def get_by_customer(self, customer_id: str) -> List[SupportCase]:
        """Get all support cases for a customer."""
        return (
            self.db.query(SupportCase)
            .filter(SupportCase.customer_id == customer_id)
            .all()
        )

    def get_by_order(self, order_id: str) -> List[SupportCase]:
        """Get all support cases for an order."""
        return self.db.query(SupportCase).filter(SupportCase.order_id == order_id).all()

    def update(self, support_case: SupportCase) -> SupportCase:
        """Update support case."""
        self.db.commit()
        self.db.refresh(support_case)
        return support_case

    def delete(self, case_id: str) -> bool:
        """Delete support case."""
        support_case = self.get_by_id(case_id)
        if support_case:
            self.db.delete(support_case)
            self.db.commit()
            return True
        return False
