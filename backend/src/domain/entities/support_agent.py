"""SupportAgent entity."""

from sqlalchemy import UUID, Column, DateTime, Enum, String
from sqlalchemy.orm import relationship

from . import Base


class SupportAgent(Base):
    __tablename__ = "support_agents"

    agent_id = Column(UUID, primary_key=True)
    email = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    role = Column(Enum("agent", "admin", name="agent_role"), nullable=False)
    created_at = Column(DateTime, nullable=False)

    # approved_refunds = relationship("RefundCase", back_populates="approved_by_agent")  # Disabled due to FK constraint issues
