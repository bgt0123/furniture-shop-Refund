#!/usr/bin/env python3
"""
Main application entry point for the Customer Support and Refund Service backend.
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from api.router import api_router
from database.session import init_db


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
    print("Starting server on http://127.0.0.1:8001")
    print("API docs available at http://127.0.0.1:8001/api/docs")

    uvicorn.run(app, host="localhost", port=3000, log_level="debug")
