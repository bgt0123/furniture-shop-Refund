import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.config import get_config
from infrastructure.logging_config import setup_logging, get_logger
from infrastructure.middleware.error_handler import error_handler
from presentation.refund_cases import router as refund_cases_router

# Load configuration
config = get_config()

# Setup logging with INFO level
setup_logging("INFO")
logger = get_logger(__name__)

# Initialize database
from infrastructure.database.database_config import init_database
init_database()

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

# Add error handling middleware - temporarily commented for debugging
# app.middleware("http")(error_handler)

# Include routers
app.include_router(refund_cases_router)

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