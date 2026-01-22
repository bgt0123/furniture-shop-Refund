"""RefundDecisionTaken event for handling refund request decisions"""

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

from ..refund_request import RefundRequestStatus
from ..value_objects.money import Money
from ..value_objects.refund_decision import RefundDecision


class RefundDecisionTaken:
    """Domain event emitted when a refund decision is taken on a request"""
    
    def __init__(self, refund_request_repository):
        self.refund_request_repository = refund_request_repository
    
    def execute(
        self,
        refund_request_id: str,
        agent_id: str,
        decision: RefundDecision,
        refund_amount: Optional[Money] = None,
        refund_method: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute the refund decision taken event
        
        Args:
            refund_request_id: The refund request ID being decided
            agent_id: ID of the agent making the decision
            decision: Refund decision value object (contains decision type and reason)
            refund_amount: Refund amount (required for accepted decisions)
            refund_method: Refund method (required for accepted decisions)
            
        Returns:
            Dictionary with decision details and updated request status
        """
        # Validate inputs
        if not refund_request_id or not agent_id:
            raise ValueError("Refund request ID and agent ID are required")
        
        if decision.decision.name == "ACCEPTED":
            if refund_amount is None:
                raise ValueError("Refund amount is required for accepted decisions")
            if refund_method is None:
                raise ValueError("Refund method is required for accepted decisions")
        
        # Find the refund request
        refund_request = self.refund_request_repository.find_by_id(refund_request_id)
        if not refund_request:
            raise ValueError(f"Refund request {refund_request_id} not found")
        
        # Update the refund request based on decision type
        if decision.decision.name == "ACCEPTED":
            refund_request.approve(agent_id, decision.reason, refund_amount)
            status = RefundRequestStatus.APPROVED
            decision_action = "accepted"
        elif decision.decision.name == "REJECTED":
            refund_request.reject(agent_id, decision.reason)
            status = RefundRequestStatus.REJECTED
            decision_action = "rejected"
        elif decision.decision.name == "NEED_MORE_INPUT":
            refund_request.request_additional_evidence(agent_id, decision.reason)
            status = RefundRequestStatus.UNDER_REVIEW
            decision_action = "requires more input"
        else:
            raise ValueError(f"Invalid decision type: {decision.decision.value}")
        
        # Update the refund request's timestamp
        refund_request.updated_at = datetime.utcnow()
        
        # Save the updated refund request
        self.refund_request_repository.save(refund_request)
        
        # Generate decision ID
        decision_id = f"DEC-{uuid4().hex[:8].upper()}"
        
        print(f"Refund decision taken: Request {refund_request_id} {decision_action} by agent {agent_id}")
        
        return {
            "decision_id": decision_id,
            "refund_request_id": refund_request_id,
            "agent_id": agent_id,
            "decision": decision.to_dict(),
            "reason": decision.reason,
            "refund_amount": refund_amount.to_dict() if refund_amount else None,
            "refund_method": refund_method,
            "new_status": status.value,
            "timestamp": refund_request.updated_at.isoformat(),
            "refund_request": refund_request
        }