from typing import Optional, List
from uuid import UUID
from database.session import get_db
from models.support_agent import SupportAgent, AgentRole


class AgentRepository:
    """Repository for agent data access."""

    def __init__(self, db_session):
        self.db = db_session

    def get_agent(self, agent_id: UUID) -> Optional[SupportAgent]:
        """Get agent by ID."""
        return (
            self.db.query(SupportAgent).filter(SupportAgent.id == str(agent_id)).first()
        )

    def get_agent_by_email(self, email: str) -> Optional[SupportAgent]:
        """Get agent by email."""
        return self.db.query(SupportAgent).filter(SupportAgent.email == email).first()

    def get_all_agents(self) -> List[SupportAgent]:
        """Get all agents."""
        return (
            self.db.query(SupportAgent).filter(SupportAgent.is_active == "Active").all()
        )

    def create_agent(
        self, name: str, email: str, role: str = "Regular"
    ) -> SupportAgent:
        """Create a new agent."""
        agent = SupportAgent()
        agent.name = name
        agent.email = email
        agent.role = AgentRole(role)
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def save_agent(self, agent: SupportAgent) -> SupportAgent:
        """Save agent changes."""
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def deactivate_agent(self, agent_id: UUID) -> Optional[SupportAgent]:
        """Deactivate agent."""
        agent = self.get_agent(agent_id)
        if agent:
            agent.deactivate()
            return self.save_agent(agent)
        return None

    def activate_agent(self, agent_id: UUID) -> Optional[SupportAgent]:
        """Activate agent."""
        agent = self.get_agent(agent_id)
        if agent:
            agent.activate()
            return self.save_agent(agent)
        return None
