"""Environment-aware configuration for Refund Service"""

import os
from typing import Optional
from functools import lru_cache


class Config:
    """Configuration class for Refund Service"""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development").lower()
        
        # Database
        self.refund_db_path = os.getenv("REFUND_DB_PATH", "data/refund.db")
        
        # Service
        self.service_port = int(os.getenv("REFUND_SERVICE_PORT", "8001"))
        self.service_host = os.getenv("REFUND_SERVICE_HOST", "0.0.0.0")
        
        # External services
        self.auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://localhost:8080")
        self.shop_service_url = os.getenv("SHOP_SERVICE_URL", "http://localhost:8081")
        
        # CORS
        cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003")
        self.cors_origins = cors_origins.split(",") if "," in cors_origins else [cors_origins]
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Security
        self.auth_jwt_secret = os.getenv("AUTH_JWT_SECRET", "development-secret")
        
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return self.environment == "testing"


@lru_cache()
def get_config() -> Config:
    """Get cached configuration instance"""
    return Config()