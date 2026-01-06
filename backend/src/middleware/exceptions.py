from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception"""

    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationException(AppException):
    """Validation related exceptions"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 422, details)


class NotFoundException(AppException):
    """Resource not found exceptions"""

    def __init__(self, resource: str, identifier: str):
        super().__init__(f"{resource} with {identifier} not found", 404)


class UnauthorizedException(AppException):
    """Authentication related exceptions"""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)


class ForbiddenException(AppException):
    """Authorization related exceptions"""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, 403)


class BusinessRuleException(AppException):
    """Business rule violation exceptions"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 409, details)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "error_description": "Invalid request data",
            "details": exc.errors(),
            "path": request.url.path,
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "error_description": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path,
        },
    )


async def app_exception_handler(request: Request, exc: AppException):
    """Handle application exceptions"""
    logger.error(f"Application error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "app_error",
            "error_description": exc.message,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "server_error",
            "error_description": "Internal server error",
            "status_code": 500,
            "path": request.url.path,
        },
    )


def setup_exception_handlers(app):
    """Setup all exception handlers for the FastAPI app"""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Rate limiting middleware
    if settings.ENVIRONMENT == "production":
        from slowapi import Limiter
        from slowapi.util import get_remote_address

        limiter = Limiter(key_func=get_remote_address)
        app.state.limiter = limiter

        @app.middleware("http")
        async def rate_limit_middleware(request: Request, call_next):
            try:
                return await call_next(request)
            except Exception as e:
                logger.error(f"Rate limit error: {str(e)}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "rate_limit_exceeded",
                        "error_description": str(e),
                        "status_code": 429,
                        "path": request.url.path,
                    },
                )
