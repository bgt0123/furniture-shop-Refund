from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.auth import decode_access_token, has_required_role
from typing import Optional


class AuthMiddleware(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(AuthMiddleware, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(
            request
        )
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme",
                )
            token = credentials.credentials
            token_data = decode_access_token(token)
            if not token_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                )
            # Store token data in request state for downstream use
            request.state.user = token_data
            return token_data
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization required",
            )


def role_required(required_roles: list[str]):
    """Dependency to check if user has required roles"""

    def dependency(request: Request):
        token_data = request.state.user
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        if not has_required_role(token_data.access_token, required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )

        return token_data

    return dependency


# Customer-only access
def customer_only(request: Request):
    return role_required(["customer"])(request)


# Support agent access
def agent_only(request: Request):
    return role_required(["support_agent", "admin"])(request)


# Admin-only access
def admin_only(request: Request):
    return role_required(["admin"])(request)


# Authentication dependency for basic auth check
auth_required = AuthMiddleware()
