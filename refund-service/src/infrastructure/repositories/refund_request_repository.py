import sqlite3
from datetime import datetime
from typing import List, Optional
from ..database.database_config import get_connection
from domain.refund_request import RefundRequest
from domain.refund_request import RefundRequestStatus


class RefundRequestRepository:
    """Repository for RefundRequest aggregate persistence"""

    def save(self, refund_request: RefundRequest) -> None:
        """Save a refund request to the database"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Convert refund request to dictionary
            data = refund_request.to_dict()
            
            cursor.execute(
                """
                INSERT OR REPLACE INTO refund_requests 
                (refund_request_id, support_case_number, customer_id, product_ids, request_reason, 
                 evidence_photos, status, decision_reason, refund_amount,
                 decision_date, decision_agent_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["refund_request_id"],
                    data["support_case_number"],
                    data["customer_id"],
                    ",".join(data["product_ids"]),
                    data["request_reason"],
                    ",".join(data["evidence_photos"]),
                    data["status"],
                    data["decision_reason"],
                    str(data["refund_amount"]["amount"]) if data["refund_amount"] else None,
                    data["decision_date"],
                    data["decision_agent_id"],
                    data["created_at"]
                )
            )
            conn.commit()
            print(f"Saved refund request {refund_request.refund_request_id}")
        finally:
            conn.close()

    def find_by_id(self, refund_request_id: str) -> Optional[RefundRequest]:
        """Find a refund request by ID"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM refund_requests WHERE refund_request_id = ?",
                (refund_request_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return self._row_to_refund_request(row)
            return None
        finally:
            conn.close()

    def find_by_support_case_number(self, case_number: str) -> List[RefundRequest]:
        """Find all refund requests for a support case"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM refund_requests WHERE refund_case_id = ?",
                (case_number,)
            )
            rows = cursor.fetchall()
            
            requests = [self._row_to_refund_request(row) for row in rows if row]
            return [req for req in requests if req is not None]
        finally:
            conn.close()

    def find_by_customer_id(self, customer_id: str) -> List[RefundRequest]:
        """Find all refund requests for a customer"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM refund_requests WHERE customer_id = ?",
                (customer_id,)
            )
            rows = cursor.fetchall()
            
            requests = [self._row_to_refund_request(row) for row in rows if row]
            return [req for req in requests if req is not None]
        finally:
            conn.close()

    def find_all(self) -> List[RefundRequest]:
        """Find all refund requests"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM refund_requests")
            rows = cursor.fetchall()
            
            requests = [self._row_to_refund_request(row) for row in rows if row]
            return [req for req in requests if req is not None]
        finally:
            conn.close()

    def _row_to_refund_request(self, row) -> Optional[RefundRequest]:
        """Convert database row to RefundRequest object"""
        if not row:
            return None
            
        # Convert row to dictionary
        data = dict(row)
        
        # Parse structured data
        refund_amount = None
        if data.get("refund_amount"):
            from domain.value_objects.money import Money
            refund_amount = Money.from_dict({
                "amount": float(data["refund_amount"]),
                "currency": "USD"
            })
        
        # Parse dates from strings
        decision_date = None
        if data.get("decision_date"):
            decision_date = datetime.fromisoformat(data["decision_date"])
        
        created_at = None  
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])
        
        # Extract from comma-separated strings
        product_ids = data.get("product_ids", "").split(",") if data.get("product_ids") else []
        evidence_photos = data.get("evidence_photos", "").split(",") if data.get("evidence_photos") else []
        
        return RefundRequest(
            refund_request_id=data["refund_request_id"],
            support_case_number=data.get("support_case_number", "unknown-case"),
            customer_id=data.get("customer_id", "unknown-customer"),
            product_ids=product_ids,
            request_reason=data["request_reason"],
            evidence_photos=evidence_photos,
            status=RefundRequestStatus(data.get("status", "pending")),
            decision_reason=data.get("decision_reason", ""),
            refund_amount=refund_amount,
            decision_date=decision_date,
            decision_agent_id=data.get("decision_agent_id", "unknown-agent"),
            created_at=created_at
        )