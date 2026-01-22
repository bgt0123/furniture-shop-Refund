"""Repository for RefundResponse aggregate persistence"""

import sqlite3
from datetime import datetime
from typing import List, Optional
from ..database.database_config import get_connection
from domain.refund_response import RefundResponse, RefundMethod
from domain.value_objects.refund_decision import RefundDecision
from domain.value_objects.money import Money


class RefundResponseRepository:
    """Repository for RefundResponse aggregate persistence"""

    def save(self, refund_response: RefundResponse) -> None:
        """Save a refund response to the database"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT OR REPLACE INTO refund_responses 
                (response_id, refund_request_id, agent_id, decision_type, decision_reason, response_content,
                 attachments, refund_amount, refund_method, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    refund_response.response_id,
                    refund_response.refund_request_id,
                    refund_response.agent_id,
                    refund_response.decision.decision.value,
                    refund_response.decision.reason,
                    refund_response.response_content,
                    ",".join(refund_response.attachments) if refund_response.attachments else None,
                    str(refund_response.refund_amount.amount) if refund_response.refund_amount else None,
                    refund_response.refund_method.value if refund_response.refund_method else None,
                    refund_response.timestamp.isoformat()
                )
            )
            conn.commit()
            print(f"Saved refund response {refund_response.response_id}")
        finally:
            conn.close()

    def find_by_refund_request_id(self, refund_request_id: str) -> List[RefundResponse]:
        """Find all refund responses for a specific refund request"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM refund_responses WHERE refund_request_id = ? ORDER BY timestamp",
                (refund_request_id,)
            )
            rows = cursor.fetchall()
            
            responses = [self._row_to_refund_response(row) for row in rows if row]
            return [resp for resp in responses if resp is not None]
        finally:
            conn.close()

    def find_by_id(self, response_id: str) -> Optional[RefundResponse]:
        """Find a refund response by ID"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM refund_responses WHERE response_id = ?",
                (response_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return self._row_to_refund_response(row)
            return None
        finally:
            conn.close()

    def find_all(self) -> List[RefundResponse]:
        """Find all refund responses"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM refund_responses ORDER BY timestamp")
            rows = cursor.fetchall()
            
            responses = [self._row_to_refund_response(row) for row in rows if row]
            return [resp for resp in responses if resp is not None]
        finally:
            conn.close()

    def _row_to_refund_response(self, row) -> Optional[RefundResponse]:
        """Convert database row to RefundResponse object"""
        if not row:
            return None
            
        # Convert row to dictionary
        data = dict(row)
        
        # Parse structured data
        refund_amount = None
        if data.get("refund_amount"):
            refund_amount = Money.from_dict({
                "amount": float(data["refund_amount"]),
                "currency": "USD"
            })
        
        refund_method = None
        if data.get("refund_method"):
            refund_method = RefundMethod(data["refund_method"])
        
        # Parse attachments
        attachments = []
        if data.get("attachments"):
            attachments = data["attachments"].split(",") if data["attachments"] else []
        
        # Parse timestamp
        timestamp = datetime.utcnow()
        if data.get("timestamp"):
            timestamp = datetime.fromisoformat(data["timestamp"])
        
        # Handle legacy data
        decision_type = data.get("decision_type", data.get("response_type", ""))
        decision_reason = data.get("decision_reason", data.get("response_content", ""))
        
        decision = RefundDecision.from_string(decision_type, decision_reason)
        
        return RefundResponse(
            response_id=data["response_id"],
            refund_request_id=data["refund_request_id"],
            agent_id=data["agent_id"],
            decision=decision,
            response_content=data["response_content"],
            refund_amount=refund_amount,
            attachments=attachments,
            refund_method=refund_method,
            timestamp=timestamp
        )