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
        # Log unexpected errors with full traceback
        logger.error(f"Unexpected error: {e}", exc_info=True)
        logger.error(f"Full error details: {type(e).__name__}: {str(e)}")
        
        import traceback
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": f"An unexpected error occurred: {type(e).__name__}: {str(e)}",
                "request_id": str(request.scope.get("request_id", "unknown"))
            }
        )