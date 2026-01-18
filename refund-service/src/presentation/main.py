import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..infrastructure.config import get_config
from ..infrastructure.logging_config import setup_logging, get_logger
from ..infrastructure.middleware import error_handler
from .refund_requests import router as refund_requests_router

# Load configuration
config = get_config()

# Setup logging
setup_logging(config.log_level)
logger = get_logger(__name__)

app = FastAPI(
    title="Refund Service",
    description="Refund Service for Furniture Shop",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handling middleware
app.middleware("http")(error_handler)

# Include routers
app.include_router(refund_requests_router)

# Development mode logging
if config.is_development:
    logger.info("Running in development mode")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Refund Service is running"}

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy", "service": "refund"}