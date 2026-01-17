import uuid
from datetime import datetime
from typing import List
from enum import Enum as PyEnum
from sqlalchemy import Column, String, DateTime, Enum as SQLAlchemyEnum, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from database.session import Base


class AgentRole(str, PyEnum):
    """Support agent role enum."""

    REGULAR = "Regular"
    SENIOR = "Senior"
    MANAGER = "Manager"
    ADMIN = "Admin"


class SupportAgent(Base):
    """Support agent domain model."""

    __tablename__ = "support_agents"

    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    role = Column(
        SQLAlchemyEnum(AgentRole),
        default=AgentRole.REGULAR,
        nullable=False,
        server_default="Regular",
    )
    permissions = Column(JSON, default=[], nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        if self.role:
            return f"<SupportAgent {self.id} - {self.name} - {self.role.value}>"
        return f"<SupportAgent {self.id} - {self.name}>"

    def has_permission(self, permission: str) -> bool:
        """Check if agent has specific permission."""
        return permission in self.permissions

    def can_process_refund(self) -> bool:
        """Check if agent can process refunds."""
        return self.is_active and self.has_permission("process_refunds")

    def can_approve_refund(self) -> bool:
        """Check if agent can approve refunds."""
        return self.is_active and (
            self.role in [AgentRole.SENIOR, AgentRole.MANAGER, AgentRole.ADMIN]
            or self.has_permission("approve_refunds")
        )

    def deactivate(self):
        """Deactivate agent."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self):
        """Activate agent."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
