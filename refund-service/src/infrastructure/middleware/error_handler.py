"""Error handling middleware for Refund Service"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


async def error_handler(request: Request, call_next):
    """Global error handler middleware"""
    try:
        response = await call_next(request)
        return response
        
    except HTTPException as e:
        # FastAPI's HTTP exceptions - pass through
        raise e
        
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error: {e}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "request_id": str(request.scope.get("request_id", "unknown"))
            }
        )