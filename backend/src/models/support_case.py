from sqlalchemy import Column, String, Text, DateTime, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
import uuid
from typing import Optional, List, Dict, Any

Base = declarative_base()


class SupportCaseStatus(str, enum.Enum):
    OPEN = "Open"
    CLOSED = "Closed"


class SupportCase(Base):
    __tablename__ = "support_cases"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, index=True)
    order_id = Column(String, index=True)
    issue_description = Column(Text)
    status = Column(Enum(SupportCaseStatus), default=SupportCaseStatus.OPEN)
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    products = Column(JSON)  # Array of {product_id, quantity, name, price}
    attachments = Column(JSON)  # Array of {id, name, url}
    history = Column(JSON)  # Array of {action, timestamp, user_id, details}

    def __repr__(self):
        return f"<SupportCase {self.id} - {self.status}>"

    def add_history_entry(self, action: str, user_id: str, details: Dict[str, Any]):
        """Add a history entry to the case"""
        current_history = self.history or []
        current_history.append(
            {
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "details": details,
            }
        )
        self.history = current_history

    def close_case(self):
        """Close the support case"""
        if self.status == SupportCaseStatus.CLOSED:
            raise ValueError("Case is already closed")
        self.status = SupportCaseStatus.CLOSED
        self.closed_at = datetime.utcnow()
        self.add_history_entry("case_closed", "system", {"status": "Closed"})

    def can_be_closed(self) -> bool:
        """Check if case can be closed (no pending refunds)"""
        # This would be implemented with actual refund checking logic
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "order_id": self.order_id,
            "issue_description": self.issue_description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "products": self.products or [],
            "attachments": self.attachments or [],
            "history": self.history or [],
        }

    @classmethod
    def create_from_data(
        cls,
        customer_id: str,
        order_id: str,
        issue_description: str,
        products: List[Dict[str, Any]],
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> "SupportCase":
        """Factory method to create SupportCase from input data"""
        case = cls(
            customer_id=customer_id,
            order_id=order_id,
            issue_description=issue_description,
            products=products,
            attachments=attachments or [],
        )
        case.add_history_entry("case_created", customer_id, {"initial_status": "Open"})
        return case
