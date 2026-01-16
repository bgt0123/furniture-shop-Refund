import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging():
    """Setup application logging."""
    # Use absolute path to avoid multiple log files
    log_path = Path(__file__).parent.parent.parent / "support_refund.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler(
                str(log_path),
                maxBytes=1024 * 1024 * 5,  # 5 MB
                backupCount=5,
            ),
        ],
    )

    return logging.getLogger(__name__)


logger = setup_logging()
