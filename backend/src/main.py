from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.infrastructure.auth.auth_middleware import AuthMiddleware
from src.infrastructure.auth.jwt import JWTService, JWTConfig
from src.infrastructure.config.config import settings
from src.infrastructure.logging.logger import setup_logging
from src.infrastructure.errors.exceptions import (
    business_exception_handler,
    BusinessException,
)
from src.infrastructure.database.database import create_tables

# Setup logging
setup_logging()

# Create database tables
create_tables()

app = FastAPI(
    title="Furniture Shop Refund Microservice",
    description="Customer support and refund processing system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add exception handler
app.add_exception_handler(BusinessException, business_exception_handler)

# Configure JWT
jwt_config = JWTConfig(
    secret_key=settings.jwt_secret_key,
    algorithm=settings.jwt_algorithm,
    access_token_expire_minutes=settings.jwt_access_token_expire_minutes,
    refresh_token_expire_days=settings.jwt_refresh_token_expire_days,
)
jwt_service = JWTService(jwt_config)

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication middleware
app.middleware("http")(AuthMiddleware(jwt_service))

# Import and include routers
from src.api.endpoints.auth import router as auth_router
from src.api.endpoints.support_cases import router as support_cases_router
from src.api.endpoints.refund_cases import router as refund_cases_router

app.include_router(auth_router)
app.include_router(support_cases_router)
app.include_router(refund_cases_router)


@app.get("/")
async def root():
    return {"message": "Furniture Shop Refund Microservice API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "refund-microservice"}


@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import FileResponse

    return FileResponse("src/static/favicon.ico")
