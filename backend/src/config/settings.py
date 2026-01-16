from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings."""

    app_name: str = "Customer Support and Refund Service"
    app_version: str = "0.1.0"
    app_description: str = "API for managing customer support cases and refund requests"

    # Database settings
    database_url: str = "sqlite:///./support_refund.db"

    # Redis settings
    redis_url: str = "redis://localhost:6379/0"

    # JWT settings
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Logging settings
    log_level: str = "info"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
