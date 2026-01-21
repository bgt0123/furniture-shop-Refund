
import sqlite3
from typing import List, Optional
from uuid import uuid4
from ..database.database_config import get_connection


class RefundCaseRepository:
    """Repository for RefundCase aggregate persistence"""

    def save(self, refund_case) -> None:
        """Save a refund case to the database"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO refund_cases 
                (refund_case_id, case_number, customer_id, order_id, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    refund_case.refund_case_id,
                    refund_case.case_number,
                    refund_case.customer_id,
                    refund_case.order_id,
                    refund_case.status.value if hasattr(refund_case.status, 'value') else refund_case.status,
                    refund_case.created_at.isoformat() if hasattr(refund_case.created_at, 'isoformat') else refund_case.created_at,
                    refund_case.updated_at.isoformat() if hasattr(refund_case.updated_at, 'isoformat') else refund_case.updated_at
                )
            )
            conn.commit()
            print(f"Saved refund case {refund_case.refund_case_id}")
        finally:
            conn.close()

    def find_by_case_id(self, refund_case_id: str):
        """Find a refund case by ID"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM refund_cases WHERE refund_case_id = ?",
                (refund_case_id,)
            )
            row = cursor.fetchone()
            
            if row:
                print(f"Found refund case {refund_case_id}")
                print(f"Row data: {row}")
                # Return a simple object with the required attributes
                class SimpleRefundCase:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                return SimpleRefundCase(dict(row))
            else:
                print(f"Refund case {refund_case_id} not found")
                return None
        finally:
            conn.close()

    def find_by_customer_id(self, customer_id: str) -> List:
        """Find all refund cases for a customer"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM refund_cases WHERE customer_id = ?",
                (customer_id,)
            )
            rows = cursor.fetchall()
            
            print(f"Found {len(rows)} refund cases for customer {customer_id}")
            
            cases = []
            for row in rows:
                class SimpleRefundCase:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                cases.append(SimpleRefundCase(dict(row)))
            
            return cases
        finally:
            conn.close()

    def find_all(self) -> List:
        """Find all refund cases"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM refund_cases")
            rows = cursor.fetchall()
            
            print(f"Found {len(rows)} total refund cases")
            
            cases = []
            for row in rows:
                class SimpleRefundCase:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                cases.append(SimpleRefundCase(dict(row)))
            
            return cases
        finally:
            conn.close()

    def update_status(self, refund_case_id: str, new_status: str) -> bool:
        """Update the status of a refund case"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE refund_cases SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE refund_case_id = ?",
                (new_status, refund_case_id)
            )
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"Successfully updated refund case {refund_case_id} status to {new_status}")
                return True
            else:
                print(f"Failed to update refund case {refund_case_id} - not found")
                return False
        finally:
            conn.close()

    def delete_by_case_id(self, refund_case_id: str) -> bool:
        """Delete a refund case by ID"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM refund_cases WHERE refund_case_id = ?",
                (refund_case_id,)
            )
            conn.commit()
            deleted = cursor.rowcount > 0
            
            if deleted:
                print(f"Deleted refund case {refund_case_id}")
            else:
                print(f"Refund case {refund_case_id} not found for deletion")
            
            return deleted
        finally:
            conn.close()