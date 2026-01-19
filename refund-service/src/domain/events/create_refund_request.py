"""CreateRefundRequest use case implementation"""

from typing import Dict, Any, List, Optional
from uuid import uuid4

from ..refund_case import RefundCase
from ..refund_request import RefundRequestStatus


class CreateRefundRequest:
    """Use case for creating a new refund request"""

    def __init__(self, refund_case_repository, support_case_repository):
        """Initialize with required dependencies"""
        self.refund_case_repository = refund_case_repository
        self.support_case_repository = support_case_repository

    def execute(
        self,
        case_number: str,
        customer_id: str,
        order_id: str,
        product_ids: List[str],
        request_reason: str,
        evidence_photos: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Execute the create refund request use case"""
        
        # Validate inputs
        if not case_number or not customer_id or not order_id:
            raise ValueError("Case number, customer ID, and order ID are required")
        
        if not product_ids:
            raise ValueError("At least one product ID is required")
        
        if not request_reason:
            raise ValueError("Request reason is required")
        
        # Check if support case exists and is not closed
        support_case = self.support_case_repository.find_by_case_number(case_number)
        
        if not support_case:
            raise ValueError(f"Support case {case_number} not found")
        
        # Check if support case is closed
        if support_case.is_closed:
            raise ValueError(f"Cannot create refund request for closed support case {case_number}")
        
        # Generate refund case ID
        refund_case_id = f"RC-{uuid4().hex[:8].upper()}"
        
        # Create RefundCase aggregate
        refund_case = RefundCase(
            refund_case_id=refund_case_id,
            case_number=case_number,
            customer_id=customer_id,
            order_id=order_id,
            status=RefundRequestStatus.PENDING
        )
        
        # Create and add refund request
        refund_case.add_refund_request(
            product_ids=product_ids,
            request_reason=request_reason,
            evidence_photos=evidence_photos or []
        )
        
        # Save to repository
        self.refund_case_repository.save(refund_case)
        
        return {
            "refund_case_id": refund_case_id,
            "status": "created",
            "refund_case": refund_case
        }