"""RefundDecisionTaken event for handling refund request decisions"""

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

from ..refund_request import RefundRequestStatus
from ..value_objects.money import Money


class RefundDecisionTaken:
    """Domain event emitted when a refund decision is taken on a request"""
    
    def __init__(self, refund_request_repository):
        self.refund_request_repository = refund_request_repository
    
    def execute(
        self,
        refund_request_id: str,
        agent_id: str,
        decision_type: str,
        decision_content: str,
        refund_amount: Optional[Money] = None,
        refund_method: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute the refund decision taken event
        
        Args:
            refund_request_id: The refund request ID being decided
            agent_id: ID of the agent making the decision
            decision_type: Type of decision ("approval", "rejection", "request_additional_evidence")
            decision_content: Content/explanation of the decision
            refund_amount: Refund amount (required for approvals)
            refund_method: Refund method (required for approvals)
            
        Returns:
            Dictionary with decision details and updated request status
        """
        # Validate inputs
        if not refund_request_id or not agent_id:
            raise ValueError("Refund request ID and agent ID are required")
        
        if decision_type == "approval":
            if refund_amount is None:
                raise ValueError("Refund amount is required for approval decisions")
            if refund_method is None:
                raise ValueError("Refund method is required for approval decisions")
        
        # Find the refund request
        refund_request = self.refund_request_repository.find_by_id(refund_request_id)
        if not refund_request:
            raise ValueError(f"Refund request {refund_request_id} not found")
        
        # Update the refund request based on decision type
        if decision_type == "approval":
            refund_request.approve(agent_id, decision_content, refund_amount)
            status = RefundRequestStatus.APPROVED
            decision_action = "approved"
        elif decision_type == "rejection":
            refund_request.reject(agent_id, decision_content)
            status = RefundRequestStatus.REJECTED
            decision_action = "rejected"
        elif decision_type == "request_additional_evidence":
            refund_request.request_additional_evidence(agent_id, decision_content)
            status = RefundRequestStatus.UNDER_REVIEW
            decision_action = "requested additional evidence"
        else:
            raise ValueError(f"Invalid decision type: {decision_type}")
        
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
            "decision_type": decision_type,
            "decision_content": decision_content,
            "refund_amount": refund_amount.to_dict() if refund_amount else None,
            "refund_method": refund_method,
            "new_status": status.value,
            "timestamp": refund_request.updated_at.isoformat(),
            "refund_request": refund_request
        }