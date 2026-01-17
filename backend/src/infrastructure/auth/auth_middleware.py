"""Authentication middleware."""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional

from .jwt import JWTService, JWTConfig


class AuthMiddleware:
    """Authentication middleware for FastAPI."""

    def __init__(self, jwt_service: JWTService):
        self.jwt_service = jwt_service

    async def __call__(self, request: Request, call_next):
        # Skip authentication for certain paths
        if request.url.path in [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/auth/login",
            "/auth/test-login",
            "/auth/refresh",
            "/auth/logout",
        ]:
            return await call_next(request)

        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid authorization header"},
            )

        token = authorization.replace("Bearer ", "")
        token_data = self.jwt_service.verify_token(token)

        if not token_data:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
            )

        # Add user info to request state
        request.state.user_id = token_data.user_id
        request.state.email = token_data.email
        request.state.role = token_data.role

        response = await call_next(request)
        return response


def get_current_user(request: Request):
    """Dependency to get current user from request."""
    if not hasattr(request.state, "user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return {
        "user_id": request.state.user_id,
        "email": request.state.email,
        "role": request.state.role,
    }
