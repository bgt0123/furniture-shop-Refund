import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, JSON, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from database.session import Base


class SupportCaseStatus(str, Enum):
    """Support case status enum."""

    OPEN = "Open"
    CLOSED = "Closed"


class SupportCase(Base):
    """Support case domain model."""

    __tablename__ = "support_cases"

    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    customer_id = Column(String(36), nullable=False, index=True)
    order_id = Column(String(36), nullable=False, index=True)
    products = Column(JSON, nullable=False)
    issue_description = Column(Text, nullable=False)
    status = Column(
        SQLAlchemyEnum(SupportCaseStatus),
        default=SupportCaseStatus.OPEN,
        nullable=False,
        server_default=SupportCaseStatus.OPEN.name,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    attachments = Column(JSON, default=[], nullable=False)

    def __repr__(self):
        return f"<SupportCase {self.id} - {self.status.value}>"

    def close(self):
        """Close the support case."""
        if self.status == SupportCaseStatus.OPEN:
            self.status = SupportCaseStatus.CLOSED
            self.closed_at = datetime.utcnow()

    def can_close(self) -> bool:
        """Check if support case can be closed."""
        # TODO: Check for pending refund cases
        return True

    def add_attachment(self, attachment: Dict[str, Any]):
        """Add attachment to support case."""
        self.attachments.append(attachment)
