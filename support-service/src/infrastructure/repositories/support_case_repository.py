"""SupportCase repository implementation"""

import sqlite3
from typing import List, Optional
from ..database.database_config import get_connection


class SupportCaseRepository:
    """Repository for SupportCase aggregate persistence"""
    
    def save(self, support_case) -> None:
        """Save a support case to the database"""
        import sys
        print(f"DEBUG: Starting save for case {support_case.case_number}", file=sys.stderr)
        print(f"DEBUG: Case has comments attribute: {hasattr(support_case, 'comments')}", file=sys.stderr)
        if hasattr(support_case, 'comments'):
            print(f"DEBUG: Number of comments: {len(support_case.comments) if support_case.comments else 'None'}", file=sys.stderr)
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO support_cases 
                (case_number, customer_id, case_type, subject, description, status, 
                 refund_request_id, assigned_agent_id, created_at, updated_at,
                 order_id, product_ids, delivery_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    support_case.case_number,
                    support_case.customer_id,
                    support_case.case_type.value,
                    support_case.subject,
                    support_case.description,
                    support_case.status.value,
                    ",".join(support_case.refund_request_ids) if support_case.refund_request_ids else None,
                    support_case.assigned_agent_id,
                    support_case.created_at.isoformat(),
                    support_case.updated_at.isoformat(),
                    support_case.order_id,
                    ",".join(support_case.product_ids) if support_case.product_ids else None,
                    support_case.delivery_date.isoformat() if support_case.delivery_date else None
                )
            )
            
            # Save comments
            print(f"DEBUG: Checking comments to save...", file=sys.stderr)
            if hasattr(support_case, 'comments'):
                print(f"DEBUG: Case has comments attribute", file=sys.stderr)
                if support_case.comments:
                    print(f"Saving {len(support_case.comments)} comments for case {support_case.case_number}", file=sys.stderr)
                    # First delete existing comments for this case
                    cursor.execute("DELETE FROM support_comments WHERE case_number = ?", (support_case.case_number,))
                    
                    # Then insert all current comments
                    for i, comment in enumerate(support_case.comments):
                        print(f"  Saving comment {i}: id={comment.comment_id}", file=sys.stderr)
                        cursor.execute(
                        """
                        INSERT INTO support_comments 
                        (comment_id, case_number, author_id, author_type, content, 
                         comment_type, attachments, is_internal, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            comment.comment_id,
                            comment.case_number,
                            comment.author_id,
                            comment.author_type,
                            comment.content,
                            comment.comment_type.value if hasattr(comment.comment_type, 'value') else comment.comment_type,
                            ",".join(comment.attachments) if comment.attachments else None,
                            comment.is_internal,
                            comment.timestamp.isoformat()
                        )
                    )
            
            conn.commit()
            print(f"Saved support case {support_case.case_number} with {len(getattr(support_case, 'comments', []))} comments")
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
            
            if not row:
                return None
            
            # Import domain objects
            from domain.support_case import SupportCase, CaseType, CaseStatus
            from domain.comment import Comment, CommentType
            from datetime import datetime
            
            data = dict(row)
            
            # Convert string enums to proper Enum objects
            case_type = CaseType(data["case_type"]) if data["case_type"] in ["question", "refund"] else CaseType.QUESTION
            status = CaseStatus(data["status"]) if data["status"] in ["open", "in_progress", "closed"] else CaseStatus.OPEN
            
            # Convert string dates to datetime objects
            created_at = datetime.fromisoformat(data["created_at"]) if data["created_at"] else datetime.utcnow()
            updated_at = datetime.fromisoformat(data["updated_at"]) if data["updated_at"] else datetime.utcnow()
            
            # Parse product_ids and delivery_date
            product_ids = []
            if data["product_ids"]:
                product_ids = data["product_ids"].split(",") if data["product_ids"] else []
            
            delivery_date = None
            if data["delivery_date"]:
                delivery_date = datetime.fromisoformat(data["delivery_date"])
            
            # Load comments
            cursor.execute(
                "SELECT * FROM support_comments WHERE case_number = ? ORDER BY timestamp",
                (case_number,)
            )
            comment_rows = cursor.fetchall()
            comments = []
            
            for comment_row in comment_rows:
                comment_data = dict(comment_row)
                comment_type = CommentType(comment_data["comment_type"]) if comment_data["comment_type"] in ["customer_comment", "agent_response", "refund_feedback"] else CommentType.CUSTOMER_COMMENT
                timestamp = datetime.fromisoformat(comment_data["timestamp"]) if comment_data["timestamp"] else datetime.utcnow()
                attachments = []
                if comment_data["attachments"]:
                    attachments = comment_data["attachments"].split(",") if comment_data["attachments"] else []
                
                comment = Comment(
                    comment_id=comment_data["comment_id"],
                    case_number=comment_data["case_number"],
                    author_id=comment_data["author_id"],
                    author_type=comment_data["author_type"],
                    content=comment_data["content"],
                    comment_type=comment_type,
                    attachments=attachments,
                    timestamp=timestamp,
                    is_internal=comment_data["is_internal"]
                )
                comments.append(comment)
            
            # Parse refund_request_ids
            refund_request_ids = []
            if data["refund_request_id"]:
                refund_request_ids = data["refund_request_id"].split(",") if data["refund_request_id"] else []
            
            support_case = SupportCase(
                case_number=data["case_number"],
                customer_id=data["customer_id"],
                case_type=case_type,
                subject=data["subject"],
                description=data["description"],
                refund_request_ids=refund_request_ids,
                status=status,
                created_at=created_at,
                updated_at=updated_at,
                assigned_agent_id=data["assigned_agent_id"],
                order_id=data["order_id"],
                product_ids=product_ids,
                delivery_date=delivery_date,
                comments=comments
            )
            
            return support_case
            
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
            from domain.comment import Comment, CommentType
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
                
                # Parse product_ids and delivery_date
                product_ids = []
                if data["product_ids"]:
                    product_ids = data["product_ids"].split(",") if data["product_ids"] else []
                
                delivery_date = None
                if data["delivery_date"]:
                    delivery_date = datetime.fromisoformat(data["delivery_date"])
                
                # Load comments for this case
                cursor.execute(
                    "SELECT * FROM support_comments WHERE case_number = ? ORDER BY timestamp",
                    (data["case_number"],)
                )
                comment_rows = cursor.fetchall()
                comments = []
                
                for comment_row in comment_rows:
                    comment_data = dict(comment_row)
                    comment_type = CommentType(comment_data["comment_type"]) if comment_data["comment_type"] in ["customer_comment", "agent_response", "refund_feedback"] else CommentType.CUSTOMER_COMMENT
                    timestamp = datetime.fromisoformat(comment_data["timestamp"]) if comment_data["timestamp"] else datetime.utcnow()
                    attachments = []
                    if comment_data["attachments"]:
                        attachments = comment_data["attachments"].split(",") if comment_data["attachments"] else []
                    
                    comment = Comment(
                        comment_id=comment_data["comment_id"],
                        case_number=comment_data["case_number"],
                        author_id=comment_data["author_id"],
                        author_type=comment_data["author_type"],
                        content=comment_data["content"],
                        comment_type=comment_type,
                        attachments=attachments,
                        timestamp=timestamp,
                        is_internal=comment_data["is_internal"]
                    )
                    comments.append(comment)
                
                # Parse refund_request_ids
                refund_request_ids = []
                if data["refund_request_id"]:
                    refund_request_ids = data["refund_request_id"].split(",") if data["refund_request_id"] else []
                
                case = SupportCase(
                    case_number=data["case_number"],
                    customer_id=data["customer_id"],
                    case_type=case_type,
                    subject=data["subject"],
                    description=data["description"],
                    refund_request_ids=refund_request_ids,
                    status=status,
                    created_at=created_at,
                    updated_at=updated_at,
                    assigned_agent_id=data["assigned_agent_id"],
                    order_id=data["order_id"],
                    product_ids=product_ids,
                    delivery_date=delivery_date,
                    comments=comments
                )
                cases.append(case)
            
            return cases
        finally:
            conn.close()

    def find_all(self) -> List:
        """Find all support cases"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM support_cases")
            rows = cursor.fetchall()
            
            print(f"Found {len(rows)} total support cases")
            
            # Import domain objects
            from domain.support_case import SupportCase, CaseType, CaseStatus
            from domain.comment import Comment, CommentType
            from datetime import datetime
            
            cases = []
            for row in rows:
                data = dict(row)
                
                # Convert string enums to proper Enum objects
                try:
                    case_type = CaseType(data.get('case_type'))
                except:
                    case_type = CaseType.QUESTION
                
                try:
                    status = CaseStatus(data.get('status'))
                except:
                    status = CaseStatus.OPEN
                
                # Parse refund_request_ids
                refund_request_ids = []
                refund_request_id_str = data.get('refund_request_id')
                if refund_request_id_str:
                    refund_request_ids = refund_request_id_str.split(",") if refund_request_id_str else []
                
                # Parse product_ids
                product_ids = []
                product_ids_str = data.get('product_ids')
                if product_ids_str:
                    product_ids = product_ids_str.split(",") if product_ids_str else []
                
                # Handle dates
                created_at_str = data.get('created_at')
                updated_at_str = data.get('updated_at')
                created_at = datetime.fromisoformat(created_at_str) if created_at_str else datetime.utcnow()
                updated_at = datetime.fromisoformat(updated_at_str) if updated_at_str else datetime.utcnow()
                
                # Create SupportCase object
                support_case = SupportCase(
                    case_number=data.get('case_number', ''),
                    customer_id=data.get('customer_id', ''),
                    case_type=case_type,
                    subject=data.get('subject', ''),
                    description=data.get('description', ''),
                    status=status,
                    refund_request_ids=refund_request_ids,
                    assigned_agent_id=data.get('assigned_agent_id'),
                    order_id=data.get('order_id'),
                    product_ids=product_ids,
                    delivery_date=data.get('delivery_date'),
                    created_at=created_at,
                    updated_at=updated_at
                )
                
                cases.append(support_case)
            
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