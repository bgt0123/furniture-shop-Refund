"""OrderReference entity for referencing external order systems."""

from sqlalchemy import UUID, Column, DateTime, String
from sqlalchemy.orm import relationship

from . import Base


class OrderReference(Base):
    """Reference to an external order."""

    __tablename__ = "order_references"

    order_id = Column(UUID, primary_key=True)
    external_order_id = Column(String(255), nullable=False, unique=True)
    customer_id = Column(UUID, nullable=False)
    created_at = Column(DateTime, nullable=False)

    # This would typically link to support cases or refund cases
    # support_cases = relationship("SupportCase", back_populates="order_reference")  # Disabled due to FK constraint issues
