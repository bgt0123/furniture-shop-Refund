"""Customer entity."""

from sqlalchemy import UUID, Column, DateTime, String
from sqlalchemy.orm import relationship

from . import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(UUID, primary_key=True)
    email = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    created_at = Column(DateTime, nullable=False)

    support_cases = relationship("SupportCase", back_populates="customer")
