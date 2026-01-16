"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from src.infrastructure.auth.jwt import JWTService, JWTConfig, TokenData

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# JWT configuration
jwt_config = JWTConfig(
    secret_key="your-secret-key-here",  # Should be loaded from env
    access_token_expire_minutes=30,
    refresh_token_expire_days=7,
)
jwt_service = JWTService(jwt_config)


class LoginRequest(BaseModel):
    """Login request model."""

    email: str
    password: str


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Refresh token request model."""

    refresh_token: str


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate user and return tokens."""
    # TODO: Implement actual user authentication
    # For now, create mock tokens
    token_data = TokenData(user_id="user-123", email=request.email, role="customer")

    access_token = jwt_service.create_access_token(token_data)
    refresh_token = jwt_service.create_refresh_token(token_data)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest):
    """Refresh access token using refresh token."""
    new_access_token = jwt_service.refresh_access_token(request.refresh_token)
    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    return TokenResponse(
        access_token=new_access_token, refresh_token=request.refresh_token
    )


@router.post("/logout")
async def logout():
    """Logout user (in real implementation, would blacklist token)."""
    return {"message": "Successfully logged out"}
