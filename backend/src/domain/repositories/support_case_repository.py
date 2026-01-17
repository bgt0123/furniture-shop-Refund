"""SupportCase repository interface and implementation."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..entities.support_case import SupportCase


class SupportCaseRepository(ABC):
    """Abstract interface for SupportCase repository."""

    @abstractmethod
    def save(self, support_case: SupportCase) -> None:
        """Save a support case."""
        pass

    @abstractmethod
    def find_by_id(self, case_id: UUID) -> Optional[SupportCase]:
        """Find support case by ID."""
        pass

    @abstractmethod
    def find_by_customer_id(self, customer_id: UUID) -> List[SupportCase]:
        """Find support cases by customer ID."""
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[SupportCase]:
        """Find support cases by status."""
        pass

    @abstractmethod
    def update_status(self, case_id: UUID, status: str) -> bool:
        """Update support case status."""
        pass


class SQLAlchemySupportCaseRepository(SupportCaseRepository):
    """SQLAlchemy implementation of SupportCase repository."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, support_case: SupportCase) -> None:
        """Save a support case."""
        self.session.add(support_case)
        self.session.commit()

    def find_by_id(self, case_id: UUID) -> Optional[SupportCase]:
        """Find support case by ID."""
        return (
            self.session.query(SupportCase)
            .filter(SupportCase.case_id == case_id)
            .first()
        )

    def find_by_customer_id(self, customer_id: UUID) -> List[SupportCase]:
        """Find support cases by customer ID."""
        return (
            self.session.query(SupportCase)
            .filter(SupportCase.customer_id == customer_id)
            .all()
        )

    def find_by_status(self, status: str) -> List[SupportCase]:
        """Find support cases by status."""
        return (
            self.session.query(SupportCase).filter(SupportCase.status == status).all()
        )

    def update_status(self, case_id: UUID, status: str) -> bool:
        """Update support case status."""
        support_case = self.find_by_id(case_id)
        if support_case:
            # For SQLAlchemy, we set the attribute directly
            support_case.status = status  # type: ignore
            self.session.commit()
            return True
        return False
