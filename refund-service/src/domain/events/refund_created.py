from datetime import datetime
from typing import Dict, Any
from uuid import uuid4

from ..refund import Refund, RefundStatus, RefundMethod
from ..value_objects.money import Money


class RefundCreated:
    """Domain event emitted when a refund is created"""
    
    def __init__(self, refund_repository):
        self.refund_repository = refund_repository
    
    def execute(
        self,
        refund_request_id: str,
        customer_id: str,
        order_id: str,
        amount: Money,
        method: RefundMethod,
        agent_id: str
    ) -> Dict[str, Any]:
        """Execute the refund creation event
        
        Args:
            refund_request_id: The approved refund request ID
            customer_id: Customer ID receiving the refund
            order_id: Order ID being refunded
            amount: Refund amount
            method: Refund method
            agent_id: Agent processing the refund
            
        Returns:
            Dictionary with refund details
        """
        # Validate inputs
        if not refund_request_id or not customer_id or not order_id:
            raise ValueError("Refund request ID, customer ID, and order ID are required")
        
        if amount is None:
            raise ValueError("Refund amount is required")
        
        if method is None:
            raise ValueError("Refund method is required")
        
        # Create refund aggregate using factory method
        refund = Refund.from_approved_request(
            refund_request_id=refund_request_id,
            customer_id=customer_id,
            order_id=order_id,
            amount=amount,
            method=method
        )
        
        # Note: agent_id is handled in refund response/decision tracking, not in Refund aggregate
        # Save refund to repository
        self.refund_repository.save(refund)
        
        return {
            "refund_id": refund.refund_id,
            "refund_request_id": refund_request_id,
            "customer_id": customer_id,
            "order_id": order_id,
            "amount": amount.to_dict(),
            "method": method.value,
            "status": refund.status.value,
            "created_at": refund.created_at.isoformat()
        }