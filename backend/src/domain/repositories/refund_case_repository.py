"""RefundCase repository interface and implementation."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..entities.refund_case import RefundCase
from ..entities.refund_item import RefundItem


class RefundCaseRepository(ABC):
    """Abstract interface for RefundCase repository."""

    @abstractmethod
    def save(self, refund_case: RefundCase) -> None:
        """Save a refund case."""
        pass

    @abstractmethod
    def find_by_id(self, refund_id: UUID) -> Optional[RefundCase]:
        """Find refund case by ID."""
        pass

    @abstractmethod
    def find_by_support_case_id(self, support_case_id: UUID) -> List[RefundCase]:
        """Find refund cases by support case ID."""
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[RefundCase]:
        """Find refund cases by status."""
        pass

    @abstractmethod
    def update_status(self, refund_id: UUID, status: str) -> bool:
        """Update refund case status."""
        pass


class SQLAlchemyRefundCaseRepository(RefundCaseRepository):
    """SQLAlchemy implementation of RefundCase repository."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, refund_case: RefundCase) -> None:
        """Save a refund case."""
        self.session.add(refund_case)
        self.session.commit()

    def find_by_id(self, refund_id: UUID) -> Optional[RefundCase]:
        """Find refund case by ID."""
        return (
            self.session.query(RefundCase)
            .filter(RefundCase.refund_id == refund_id)
            .first()
        )

    def find_by_support_case_id(self, support_case_id: UUID) -> List[RefundCase]:
        """Find refund cases by support case ID."""
        return (
            self.session.query(RefundCase)
            .filter(RefundCase.support_case_id == support_case_id)
            .all()
        )

    def find_by_status(self, status: str) -> List[RefundCase]:
        """Find refund cases by status."""
        return self.session.query(RefundCase).filter(RefundCase.status == status).all()

    def update_status(self, refund_id: UUID, status: str) -> bool:
        """Update refund case status."""
        refund_case = self.find_by_id(refund_id)
        if refund_case:
            # For SQLAlchemy, we set the attribute directly
            refund_case.status = status  # type: ignore
            self.session.commit()
            return True
        return False
