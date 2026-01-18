"""Authentication middleware for Support Service"""

from fastapi import Request, HTTPException, status, Depends
from typing import Optional
import httpx


async def get_current_user(request: Request) -> dict:
    """Extract and validate user from request headers"""
    
    # Get authorization header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    # Extract token (assuming Bearer token)
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required"
        )
    
    token = auth_header[7:]  # Remove "Bearer " prefix
    
    # Verify token with external auth service
    try:
        # In production, this would call the actual auth service
        # For now, we'll validate the format and extract basic info
        
        # Mock validation - extract user info from token format
        # This would normally be a JWT validation call
        if not token or len(token) < 10:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )
        
        # Mock user extraction - in real implementation
        # this would decode JWT or call auth service API
        user_info = {
            "user_id": "user-123",  # Extract from token
            "roles": ["customer"],  # Extract role information
            "email": "customer@example.com"
        }
        
        return user_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed"
        )


def require_role(required_role: str):
    """Create dependency to require specific role"""
    def role_dependency(user: dict = Depends(get_current_user)) -> dict:
        if required_role not in user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return user
    return role_dependency


def require_agent_role():
    """Shortcut for requiring agent role"""
    return require_role("agent")


def require_customer_role():
    """Shortcut for requiring customer role"""
    return require_role("customer")