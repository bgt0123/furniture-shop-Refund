"""Database connection and setup for Support Service"""

import sqlite3
import os
from typing import Optional

from ..config import get_config
from .schema import (
    CREATE_SUPPORT_CASES_TABLE,
    CREATE_SUPPORT_RESPONSES_TABLE,
    CREATE_SUPPORT_COMMENTS_TABLE,
    CREATE_SUPPORT_CASES_INDEXES,
    CREATE_SUPPORT_RESPONSES_INDEXES,
    CREATE_SUPPORT_COMMENTS_INDEXES
)

def get_database_path() -> str:
    """Get database file path"""
    config = get_config()
    return config.support_db_path


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
        # Create tables
        conn.execute(CREATE_SUPPORT_CASES_TABLE)
        conn.execute(CREATE_SUPPORT_RESPONSES_TABLE)
        conn.execute(CREATE_SUPPORT_COMMENTS_TABLE)
        
        # Create indexes
        for index_sql in CREATE_SUPPORT_CASES_INDEXES + CREATE_SUPPORT_RESPONSES_INDEXES + CREATE_SUPPORT_COMMENTS_INDEXES:
            conn.execute(index_sql)
        
        conn.commit()
        print("Support Service database initialized successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"Error initializing database: {e}")
        raise
    
    finally:
        conn.close()