#!/usr/bin/env python3
"""Entry point for Refund Service"""

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
    port = int(os.getenv("REFUND_SERVICE_PORT", "8002"))
    host = os.getenv("REFUND_SERVICE_HOST", "0.0.0.0")
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    logger = logging.getLogger("refund-service")
    logger.info(f"Starting Refund Service on {host}:{port}")
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
        logger.info("Refund Service stopped by user")
    except Exception as e:
        logger.error(f"Refund Service crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()