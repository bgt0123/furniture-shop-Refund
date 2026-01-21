"""Database connection and setup for Refund Service"""

import sqlite3
import os
from typing import Optional

from ..config import get_config
from .schema import (
    CREATE_REFUND_CASES_TABLE,
    CREATE_REFUND_REQUESTS_TABLE,
    CREATE_REFUND_RESPONSES_TABLE,
    CREATE_CASE_TIMELINE_TABLE,
    REFUND_SERVICE_INDEXES
)

def get_database_path() -> str:
    """Get database file path"""
    config = get_config()
    return config.refund_db_path

def get_connection() -> sqlite3.Connection:
    """Get database connection with proper configuration"""
    db_path = get_database_path()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    
    return conn


def init_database() -> None:
    """Initialize database with schema and indexes"""
    conn = get_connection()
    
    try:
        # Create tables with debug logging
        print("Creating refund_requests table...")
        conn.execute(CREATE_REFUND_REQUESTS_TABLE)
        
        # Create indexes
        for index_sql in REFUND_SERVICE_INDEXES:
            conn.execute(index_sql)
        
        conn.commit()
        print("Refund Service database initialized successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"Error initializing database: {e}")
        raise
    
    finally:
        conn.close()