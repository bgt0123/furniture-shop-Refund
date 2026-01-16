#!/usr/bin/env python3
"""
Main application entry point for the Customer Support and Refund Service backend.
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from api.router import api_router
from database.session import init_db


class CustomException(Exception):
    """Custom exception base class."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Customer Support and Refund Service",
        description="API for managing customer support cases and refund requests",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        """Handle custom exceptions."""
        return JSONResponse(status_code=exc.status_code, content={"error": exc.message})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle validation errors."""
        return JSONResponse(
            status_code=422,
            content={"error": "Validation error", "details": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        return JSONResponse(status_code=500, content={"error": "Internal server error"})

    # Initialize database
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")

    # Include API routers
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    import logging

    logging.basicConfig(level=logging.DEBUG)
    print("Starting server on http://localhost:3000")
    print("API docs available at http://localhost:3000/api/docs")

    uvicorn.run(app, host="localhost", port=3000, log_level="debug")
