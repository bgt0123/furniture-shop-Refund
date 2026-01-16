from fastapi import APIRouter
from .support_endpoints import router as support_router


api_router = APIRouter()


@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Include sub-routers
api_router.include_router(support_router)
