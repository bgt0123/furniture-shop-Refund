"""Database configuration and schema for Support Service"""

from .database_config import get_connection, init_database
from .schema import (
    CREATE_SUPPORT_CASES_TABLE,
    CREATE_SUPPORT_RESPONSES_TABLE,
    CREATE_SUPPORT_CASES_INDEXES,
    CREATE_SUPPORT_RESPONSES_INDEXES
)