"""Environment configuration management."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "sqlite:///./refund_service.db"

    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # External Services
    order_api_base_url: Optional[str] = None
    payment_gateway_api_base_url: Optional[str] = None
    payment_gateway_api_key: Optional[str] = None

    # Application
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:3000"
    log_level: str = "INFO"
    log_file: Optional[str] = None

    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()
