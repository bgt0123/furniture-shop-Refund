from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from src.auth import create_user_token, authenticate_user, Token
from src.api import support_endpoints, refund_endpoints, admin_endpoints
from src.middleware.exceptions import setup_exception_handlers
import logging
from logging.config import dictConfig

# Configure logging
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%%(levelprefix)s %(asctime)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%%(levelprefix)s %(asctime)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}

dictConfig(logging_config)

app = FastAPI(
    title="Customer Support and Refund Service",
    description="API for managing customer support cases and refund requests",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Setup exception handlers
setup_exception_handlers(app)

# Security setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://furnitureshop.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Authentication endpoints
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_user_token(user)
    return access_token


# Include API routers
app.include_router(support_endpoints.router, prefix="/support", tags=["Support Cases"])
app.include_router(refund_endpoints.router, prefix="/refunds", tags=["Refund Cases"])
app.include_router(admin_endpoints.router, prefix="/admin", tags=["Admin"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "support-refund"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
