"""Custom exceptions."""

from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import Optional


class BusinessException(Exception):
    """Base business exception."""

    def __init__(self, message: str, error_code: str = "BUSINESS_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class InvalidOrderException(BusinessException):
    """Invalid order exception."""

    def __init__(self, message: str, error_code: str = "INVALID_ORDER"):
        super().__init__(message, error_code)


class RefundValidationException(BusinessException):
    """Refund validation exception."""

    def __init__(self, message: str, error_code: str = "REFUND_VALIDATION_ERROR"):
        super().__init__(message, error_code)


class DeliveryWindowException(BusinessException):
    """Delivery window validation exception."""

    def __init__(self, message: str, error_code: str = "DELIVERY_WINDOW_ERROR"):
        super().__init__(message, error_code)


class AuthenticationException(BusinessException):
    """Authentication exception."""

    def __init__(self, message: str, error_code: str = "AUTHENTICATION_ERROR"):
        super().__init__(message, error_code)


async def business_exception_handler(request: Request, exc: Exception):
    """Handle business exceptions."""
    if isinstance(exc, BusinessException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error_code": exc.error_code, "message": exc.message},
        )
    # Let other exceptions be handled by FastAPI
    raise exc
