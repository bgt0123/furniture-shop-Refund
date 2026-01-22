"""Database configuration and schema for Refund Service"""

from .database_config import get_connection, init_database
from .schema import (
    CREATE_REFUND_CASES_TABLE,
    CREATE_REFUND_REQUESTS_TABLE,
    CREATE_REFUND_RESPONSES_TABLE,
    REFUND_SERVICE_INDEXES
)