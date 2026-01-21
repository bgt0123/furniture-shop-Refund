#!/usr/bin/env python3
"""Entry point for Support Service"""

import os
import sys
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from presentation.main import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main entry point"""
    port = int(os.getenv("SUPPORT_SERVICE_PORT", "8001"))
    host = os.getenv("SUPPORT_SERVICE_HOST", "0.0.0.0")
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    logger = logging.getLogger("support-service")
    logger.info(f"Starting Support Service on {host}:{port}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Auto-reload: {reload}")
    
    try:
        uvicorn.run(
            "presentation.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Support Service stopped by user")
    except Exception as e:
        logger.error(f"Support Service crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()