"""Database connection and setup for Support Service"""

import sqlite3
import os
import threading
from typing import Optional
from contextlib import contextmanager

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

# Simple thread-local storage for connection pooling
_local = threading.local()

def get_connection() -> sqlite3.Connection:
    """Get database connection with proper configuration (connection pool enabled)"""
    db_path = get_database_path()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Use thread-local connection to avoid opening new connections per thread
    if not hasattr(_local, 'connection') or _local.connection is None:
        _local.connection = sqlite3.connect(db_path)
        _local.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
        
        # Enable foreign key constraints and performance optimizations
        _local.connection.execute("PRAGMA foreign_keys = ON")
        _local.connection.execute("PRAGMA journal_mode = WAL")  # Better concurrency
        _local.connection.execute("PRAGMA synchronous = NORMAL")  # Balance safety/performance
        _local.connection.execute("PRAGMA cache_size = -64000")  # 64MB cache
        
    return _local.connection

@contextmanager
def transaction():
    """Context manager for database transactions"""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


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