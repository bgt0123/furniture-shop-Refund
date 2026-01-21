"""CreateRefundRequest use case implementation"""

from typing import Dict, Any, List, Optional
from uuid import uuid4

from ..refund_request import RefundRequest, RefundRequestStatus


class CreateRefundRequest:
    """Use case for creating a new refund request"""

    def __init__(self, refund_request_repository, support_case_repository):
        """Initialize with required dependencies"""
        self.refund_request_repository = refund_request_repository
        self.support_case_repository = support_case_repository

    def execute(
        self,
        support_case_number: str,
        customer_id: str,
        order_id: str,
        product_ids: List[str],
        request_reason: str,
        evidence_photos: Optional[List[str]] = None,
        delivery_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute the create refund request use case"""
        
        # Validate inputs
        if not support_case_number or not customer_id or not order_id:
            raise ValueError("Support case number, customer ID, and order ID are required")
        
        if not product_ids:
            raise ValueError("At least one product ID is required")
        
        if not request_reason:
            raise ValueError("Request reason is required")
        
        # Validate support case can accept refund requests
        support_case = self.support_case_repository.find_by_case_number(support_case_number)
        if not support_case:
            raise ValueError(f"Support case {support_case_number} not found")
        
        if support_case.is_deleted:
            raise ValueError(f"Cannot create refund request for deleted support case {support_case_number}")
        
        if support_case.status == "closed":
            raise ValueError(f"Cannot create refund request for closed support case {support_case_number}")
        
        if support_case.case_type != "refund":
            raise ValueError(f"Cannot create refund request for non-refund support case {support_case_number}")
        
        # Generate refund request ID
        refund_request_id = f"RR-{uuid4().hex[:8].upper()}"
        
        # Create RefundRequest aggregate
        refund_request = RefundRequest(
            refund_request_id=refund_request_id,
            support_case_number=support_case_number,
            customer_id=customer_id,
            product_ids=product_ids,
            request_reason=request_reason,
            evidence_photos=evidence_photos or [],
            status=RefundRequestStatus.PENDING
        )
        
        # Save refund request to our repository
        self.refund_request_repository.save(refund_request)
        
        return {
            "refund_request_id": refund_request_id,
            "status": "created",
            "refund_request": refund_request
        }