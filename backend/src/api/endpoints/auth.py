"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from src.infrastructure.auth.jwt import JWTService, JWTConfig, TokenData

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# JWT configuration
from src.infrastructure.config.config import settings

jwt_config = JWTConfig(
    secret_key=settings.jwt_secret_key,
    algorithm=settings.jwt_algorithm,
    access_token_expire_minutes=settings.jwt_access_token_expire_minutes,
    refresh_token_expire_days=settings.jwt_refresh_token_expire_days,
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
    token_data = TokenData(
        user_id="123e4567-e89b-12d3-a456-426614174000",
        email=request.email,
        role="customer",
    )

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


@router.post("/test-login")
async def test_login():
    """Test authentication endpoint that provides a valid JWT token."""
    # Create test customer data
    test_user = TokenData(
        user_id="123e4567-e89b-12d3-a456-426614174000",
        email="customer@example.com",
        role="customer",
    )

    # Generate access token
    access_token = jwt_service.create_access_token(test_user)
    refresh_token = jwt_service.create_refresh_token(test_user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "user_id": test_user.user_id,
            "email": test_user.email,
            "role": test_user.role,
        },
    }
