from datetime import datetime

from domain.refund_request import RefundRequest, RefundRequestStatus

from ..database.database_config import get_connection


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
                 evidence_photos, status, order_id, created_at, refund_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["refund_request_id"],
                    data["support_case_number"],
                    data["customer_id"],
                    ",".join(data["product_ids"]),
                    data["request_reason"],
                    ",".join(data["evidence_photos"]),
                    data["status"],
                    data["order_id"] or None,  # Convert empty string or None to SQL NULL
                    data["created_at"],
                    data["refund_id"] or None  # Convert empty string or None to SQL NULL
                )
            )
            conn.commit()
        finally:
            conn.close()

    def find_by_id(self, refund_request_id: str) -> RefundRequest | None:
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

    def find_by_support_case_number(self, case_number: str) -> list[RefundRequest]:
        """Find all refund requests for a support case"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM refund_requests WHERE support_case_number = ?",
                (case_number,)
            )
            rows = cursor.fetchall()

            requests = [self._row_to_refund_request(row) for row in rows if row]
            return [req for req in requests if req is not None]
        finally:
            conn.close()

    def find_by_customer_id(self, customer_id: str) -> list[RefundRequest]:
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

    def find_all(self) -> list[RefundRequest]:
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

    def _map_db_status_to_enum(self, db_status: str) -> RefundRequestStatus:
        """Map database status values to RefundRequestStatus enum"""
        status_mapping = {
            "pending": RefundRequestStatus.SUBMITTED,
            "approved": RefundRequestStatus.APPROVED,
            "rejected": RefundRequestStatus.REJECTED,
            "under_review": RefundRequestStatus.UNDER_REVIEW,
            "decision_made": RefundRequestStatus.DECISION_MADE,
            "completed": RefundRequestStatus.COMPLETED,
            "cancelled": RefundRequestStatus.CANCELLED
        }
        return status_mapping.get(db_status, RefundRequestStatus.SUBMITTED)

    def _row_to_refund_request(self, row) -> RefundRequest | None:
        """Convert database row to RefundRequest object"""
        if not row:
            return None

        # Convert row to dictionary
        data = dict(row)
        


        # Parse dates from strings
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])
        
        # Handle decision_date for backward compatibility (if present)
        decision_date = None
        if data.get("decision_date"):
            try:
                decision_date = datetime.fromisoformat(data["decision_date"])
            except ValueError:
                pass

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
            status=self._map_db_status_to_enum(data.get("status", "pending")),
            order_id=data.get("order_id"),
            created_at=created_at,
            updated_at=decision_date or created_at,  # Use decision_date if available, else created_at
            refund_id=data.get("refund_id")
        )
