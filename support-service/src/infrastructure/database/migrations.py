"""Database migration utilities for Support Service"""

import sqlite3
from .database_config import get_connection


def migrate_schema() -> None:
    """Apply database schema migrations"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Check if order_id column exists
        cursor.execute("PRAGMA table_info(support_cases)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add missing columns
        if "order_id" not in columns:
            cursor.execute("ALTER TABLE support_cases ADD COLUMN order_id TEXT")
            print("Added order_id column to support_cases table")
        
        if "product_ids" not in columns:
            cursor.execute("ALTER TABLE support_cases ADD COLUMN product_ids TEXT")
            print("Added product_ids column to support_cases table")
            
        if "delivery_date" not in columns:
            cursor.execute("ALTER TABLE support_cases ADD COLUMN delivery_date TIMESTAMP")
            print("Added delivery_date column to support_cases table")
        
        conn.commit()
        print("Schema migration completed successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration error: {e}")
        raise
    finally:
        conn.close()