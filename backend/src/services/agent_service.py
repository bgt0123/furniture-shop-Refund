from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from models.support_agent import SupportAgent
from repositories.agent_repository import AgentRepository


class AgentService:
    """Service for agent operations."""

    def __init__(self, db_session: Session):
        self.repository = AgentRepository(db_session)

    def get_agent(self, agent_id: UUID) -> Optional[SupportAgent]:
        """Get agent by ID."""
        return self.repository.get_agent(agent_id)

    def authenticate_agent(self, email: str, password: str) -> Optional[SupportAgent]:
        """Authenticate agent credentials."""
        # In a real implementation, this would check password hash
        agent = self.repository.get_agent_by_email(email)
        if agent and agent.is_active:
            # Mock authentication - always return True
            return agent
        return None

    def can_process_refund(self, agent_id: UUID) -> bool:
        """Check if agent can process refunds."""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        return agent.can_process_refund()

    def can_approve_refund(self, agent_id: UUID) -> bool:
        """Check if agent can approve refunds."""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        return agent.can_approve_refund()

    def get_customer_details(self, customer_id: UUID) -> dict:
        """Get customer details for admin view."""
        # Mock implementation - would integrate with customer service
        return {
            "id": str(customer_id),
            "name": "Mock Customer",
            "email": "customer@example.com",
        }

    def get_order_details(self, order_id: UUID) -> dict:
        """Get order details for admin view."""
        # Mock implementation - would integrate with order service
        return {
            "id": str(order_id),
            "created_at": "2024-01-01T00:00:00Z",
            "total_amount": 299.99,
            "status": "Delivered",
        }

    def create_agent(
        self, name: str, email: str, role: str = "Regular"
    ) -> SupportAgent:
        """Create a new support agent."""
        return self.repository.create_agent(name, email, role)

    def update_agent_permissions(
        self, agent_id: UUID, permissions: list
    ) -> Optional[SupportAgent]:
        """Update agent permissions."""
        agent = self.get_agent(agent_id)
        if agent:
            agent.permissions = permissions
            return self.repository.save_agent(agent)
        return None
