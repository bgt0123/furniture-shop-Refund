"""CreateRefundResponse event for handling refund response creation"""

from typing import Dict, Any, Optional
from uuid import uuid4
from datetime import datetime
from ..refund_response import RefundResponse, RefundMethod
from ..value_objects.money import Money
from ..value_objects.refund_decision import RefundDecision


class CreateRefundResponse:
    """Event for creating and persisting a refund response"""
    
    def __init__(self, refund_response_repository):
        self.refund_response_repository = refund_response_repository
    
    def execute(
        self,
        refund_request_id: str,
        agent_id: str,
        decision: RefundDecision,
        response_content: str,
        refund_amount: Optional[Money] = None,
        refund_method: Optional[RefundMethod] = None,
        attachments: Optional[list] = None
    ) -> Dict[str, Any]:
        """Execute the create refund response event
        
        Args:
            refund_request_id: The refund request ID being responded to
            agent_id: ID of the agent creating the response
            decision: Refund decision value object
            response_content: Content/message of the response
            refund_amount: Amount to refund (required for accepted decisions)
            refund_method: Method of refund (required for accepted decisions)
            attachments: List of attachment URLs
            
        Returns:
            Dictionary with response details
        """
        # Validate inputs
        if not refund_request_id or not agent_id:
            raise ValueError("Refund request ID and agent ID are required")
        
        if decision.decision.name == "ACCEPTED":
            if refund_amount is None:
                raise ValueError("Refund amount is required for accepted decisions")
            if refund_method is None:
                raise ValueError("Refund method is required for accepted decisions")
        
        # Generate unique response ID
        response_id = f"RESP-{uuid4().hex[:8].upper()}"
        
        # Create refund response
        refund_response = RefundResponse(
            response_id=response_id,
            refund_request_id=refund_request_id,
            agent_id=agent_id,
            decision=decision,
            response_content=response_content,
            refund_amount=refund_amount,
            refund_method=refund_method,
            attachments=attachments or []
        )
        
        # Save response to database
        self.refund_response_repository.save(refund_response)
        
        print(f"Created refund response {response_id} for request {refund_request_id}")
        
        return {
            "response_id": response_id,
            "refund_request_id": refund_request_id,
            "agent_id": agent_id,
            "decision": decision.to_dict(),
            "response_content": response_content,
            "refund_amount": refund_amount.to_dict() if refund_amount else None,
            "refund_method": refund_method.value if refund_method else None,
            "attachments": attachments or [],
            "timestamp": refund_response.timestamp.isoformat(),
            "refund_response": refund_response
        }