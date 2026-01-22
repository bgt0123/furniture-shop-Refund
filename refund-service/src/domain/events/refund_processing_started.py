from typing import Dict, Any
from datetime import datetime


class RefundProcessingStarted:
    """Domain event emitted when refund processing begins"""
    
    def __init__(self, refund_repository):
        self.refund_repository = refund_repository
    
    def execute(self, refund_id: str) -> Dict[str, Any]:
        """Execute the refund processing started event
        
        Args:
            refund_id: The refund ID to start processing
            
        Returns:
            Dictionary with refund processing status
        """
        if not refund_id:
            raise ValueError("Refund ID is required")
        
        # Find the refund
        refund = self.refund_repository.find_by_id(refund_id)
        if not refund:
            raise ValueError(f"Refund {refund_id} not found")
        
        # Start processing
        refund.process()
        
        # Save updated refund
        self.refund_repository.save(refund)
        
        return {
            "refund_id": refund_id,
            "status": refund.status.value,
            "processed_at": refund.processed_at.isoformat() if refund.processed_at else None
        }