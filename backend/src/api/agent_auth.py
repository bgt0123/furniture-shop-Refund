from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy.orm import Session
from services.agent_service import AgentService
from database.session import get_db


class LoginRequest(BaseModel):
    email: str
    password: str


router = APIRouter(prefix="/agent", tags=["agent_auth"])


@router.post("/login")
async def login_agent(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate agent and return token."""
    # Mock authentication - accepts any password
    agent_service = AgentService(db)
    agent = agent_service.authenticate_agent(login_data.email, login_data.password)

    if not agent:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # In a real implementation, this would be a JWT token
    # For now, we'll use a simple mock token
    return {
        "access_token": f"mock_agent_token_{agent.id}",
        "agent_id": str(agent.id),
        "agent_name": agent.name,
        "agent_role": agent.role.value,
        "token_type": "bearer",
    }


@router.get("/profile")
async def get_agent_profile(agent_id: UUID, db: Session = Depends(get_db)):
    """Get agent profile."""
    agent_service = AgentService(db)
    agent = agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {
        "id": str(agent.id),
        "name": agent.name,
        "email": agent.email,
        "role": agent.role.value,
        "is_active": agent.is_active,
        "permissions": agent.permissions,
    }
