"""Logging configuration for Refund Service"""

import logging
import sys
from typing import Optional
import os


def setup_logging(level: Optional[str] = None) -> None:
    """Setup logging configuration"""
    
    log_level_str = level or os.getenv("LOG_LEVEL", "INFO")
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Suppress SQLAlchemy logs if not in debug mode
    if log_level != logging.DEBUG:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name"""
    return logging.getLogger(name)