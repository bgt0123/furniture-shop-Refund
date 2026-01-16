"""JWT authentication and token management."""

import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from pydantic import BaseModel


class TokenData(BaseModel):
    """Token payload data."""

    user_id: str
    email: str
    role: str


class JWTConfig:
    """JWT configuration."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days


class JWTService:
    """JWT token service."""

    def __init__(self, config: JWTConfig):
        self.config = config

    def create_access_token(self, data: TokenData) -> str:
        """Create access token."""
        expire = datetime.utcnow() + timedelta(
            minutes=self.config.access_token_expire_minutes
        )
        payload = {**data.dict(), "exp": expire, "type": "access"}
        return jwt.encode(
            payload, self.config.secret_key, algorithm=self.config.algorithm
        )

    def create_refresh_token(self, data: TokenData) -> str:
        """Create refresh token."""
        expire = datetime.utcnow() + timedelta(
            days=self.config.refresh_token_expire_days
        )
        payload = {**data.dict(), "exp": expire, "type": "refresh"}
        return jwt.encode(
            payload, self.config.secret_key, algorithm=self.config.algorithm
        )

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode token."""
        try:
            payload = jwt.decode(
                token, self.config.secret_key, algorithms=[self.config.algorithm]
            )
            return TokenData(
                user_id=payload.get("user_id"),
                email=payload.get("email"),
                role=payload.get("role"),
            )
        except jwt.exceptions.InvalidTokenError:
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token."""
        token_data = self.verify_token(refresh_token)
        if not token_data:
            return None
        return self.create_access_token(token_data)
