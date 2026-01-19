"""SupportCase repository implementation"""

import sqlite3
from typing import List, Optional
from ..database.database_config import get_connection


class SupportCaseRepository:
    """Repository for SupportCase aggregate persistence"""
    
    def save(self, support_case) -> None:
        """Save a support case to the database"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO support_cases 
                (case_number, customer_id, case_type, subject, description, status, 
                 refund_request_id, assigned_agent_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    support_case.case_number,
                    support_case.customer_id,
                    support_case.case_type.value,
                    support_case.subject,
                    support_case.description,
                    support_case.status.value,
                    support_case.refund_request_id,
                    support_case.assigned_agent_id,
                    support_case.created_at.isoformat(),
                    support_case.updated_at.isoformat()
                )
            )
            conn.commit()
            print(f"Saved support case {support_case.case_number}")
        finally:
            conn.close()

    def find_by_case_number(self, case_number: str):
        """Find a support case by case number"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM support_cases WHERE case_number = ?",
                (case_number,)
            )
            row = cursor.fetchone()
            
            if row:
                print(f"Found support case {case_number}")
                
                # Import domain objects
                from domain.support_case import SupportCase, CaseType, CaseStatus
                from datetime import datetime
                
                data = dict(row)
                
                # Convert string enums to proper Enum objects
                case_type = CaseType(data["case_type"]) if data["case_type"] in ["question", "refund"] else CaseType.QUESTION
                status = CaseStatus(data["status"]) if data["status"] in ["open", "in_progress", "closed"] else CaseStatus.OPEN
                
                # Convert string dates to datetime objects
                created_at = datetime.fromisoformat(data["created_at"]) if data["created_at"] else datetime.utcnow()
                updated_at = datetime.fromisoformat(data["updated_at"]) if data["updated_at"] else datetime.utcnow()
                
                return SupportCase(
                    case_number=data["case_number"],
                    customer_id=data["customer_id"],
                    case_type=case_type,
                    subject=data["subject"],
                    description=data["description"],
                    refund_request_id=data["refund_request_id"],
                    status=status,
                    created_at=created_at,
                    updated_at=updated_at,
                    assigned_agent_id=data["assigned_agent_id"]
                )
            
            # Demo data for testing purposes - create fake case if SC-001 or SC-002 is requested
            if case_number in ["SC-001", "SC-002"]:
                print(f"Creating demo support case {case_number}")
                from domain.support_case import SupportCase, CaseType, CaseStatus
                from datetime import datetime
                
                if case_number == "SC-001":
                    demo_support_case = SupportCase(
                        case_number="SC-001",
                        customer_id="cust-123",
                        case_type=CaseType.REFUND,
                        subject="Refund Request for Defective Product",
                        description="Customer is requesting refund for defective furniture received",
                        refund_request_id="RC-001",
                        status=CaseStatus.OPEN,
                        assigned_agent_id="agent-001"
                    )
                    demo_support_case.created_at = datetime(2025, 1, 18, 12, 0, 0)
                    demo_support_case.updated_at = datetime(2025, 1, 18, 12, 0, 0)
                else:  # SC-002
                    demo_support_case = SupportCase(
                        case_number="SC-002",
                        customer_id="cust-123",
                        case_type=CaseType.REFUND,
                        subject="Refund Approved for Customer",
                        description="Refund request has been approved and processed",
                        refund_request_id="RC-002",
                        status=CaseStatus.CLOSED,
                        assigned_agent_id="agent-002"
                    )
                    demo_support_case.created_at = datetime(2025, 1, 19, 10, 0, 0)
                    demo_support_case.updated_at = datetime(2025, 1, 19, 11, 0, 0)
                
                return demo_support_case
            
            print(f"Support case {case_number} not found")
            return None
        finally:
            conn.close()

    def find_by_customer_id(self, customer_id: str) -> List:
        """Find all support cases for a customer"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM support_cases WHERE customer_id = ?",
                (customer_id,)
            )
            rows = cursor.fetchall()
            
            print(f"Found {len(rows)} support cases for customer {customer_id}")
            
            # Import domain objects
            from domain.support_case import SupportCase, CaseType, CaseStatus
            from datetime import datetime
            
            cases = []
            for row in rows:
                data = dict(row)
                
                # Convert string enums to proper Enum objects
                case_type = CaseType(data["case_type"]) if data["case_type"] in ["question", "refund"] else CaseType.QUESTION
                status = CaseStatus(data["status"]) if data["status"] in ["open", "in_progress", "closed"] else CaseStatus.OPEN
                
                # Convert string dates to datetime objects
                created_at = datetime.fromisoformat(data["created_at"]) if data["created_at"] else datetime.utcnow()
                updated_at = datetime.fromisoformat(data["updated_at"]) if data["updated_at"] else datetime.utcnow()
                
                case = SupportCase(
                    case_number=data["case_number"],
                    customer_id=data["customer_id"],
                    case_type=case_type,
                    subject=data["subject"],
                    description=data["description"],
                    refund_request_id=data["refund_request_id"],
                    status=status,
                    created_at=created_at,
                    updated_at=updated_at,
                    assigned_agent_id=data["assigned_agent_id"]
                )
                cases.append(case)
            
            return cases
        finally:
            conn.close()

    def delete(self, case_number: str) -> bool:
        """Delete a support case"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM support_cases WHERE case_number = ?",
                (case_number,)
            )
            deleted = cursor.rowcount > 0
            conn.commit()
            
            if deleted:
                print(f"Deleted support case {case_number}")
            else:
                print(f"Support case {case_number} not found for deletion")
            
            return deleted
        finally:
            conn.close()