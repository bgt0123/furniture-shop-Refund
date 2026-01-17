from fastapi import APIRouter
from .support_endpoints import router as support_router
from .refund_endpoints import (
    router as refund_router,
    support_router as support_refund_router,
)
from .admin_endpoints import router as admin_router
from .agent_auth import router as agent_auth_router
from .test_endpoints import router as test_router


api_router = APIRouter()


@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Include sub-routers
api_router.include_router(test_router)  # Test endpoints
api_router.include_router(admin_router)  # Admin endpoints - put FIRST
api_router.include_router(support_router)
api_router.include_router(support_refund_router)  # Support case refund endpoints
api_router.include_router(refund_router)  # Generic refund endpoints
api_router.include_router(agent_auth_router)  # Agent authentication
