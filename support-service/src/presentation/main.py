import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.config import get_config
from infrastructure.logging_config import setup_logging, get_logger
from infrastructure.middleware.error_handler import error_handler
from presentation.support_cases import router as support_cases_router

# Load configuration
config = get_config()

# Setup logging
setup_logging(config.log_level)
logger = get_logger(__name__)

# Initialize database
from infrastructure.database.database_config import init_database
from infrastructure.database.migrations import migrate_schema
init_database()
migrate_schema()

app = FastAPI(
    title="Support Service",
    description="Support Service for Furniture Shop",
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
app.include_router(support_cases_router)

# Development mode logging
if config.is_development:
    logger.info("Running in development mode")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Support Service is running"}

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy", "service": "support"}