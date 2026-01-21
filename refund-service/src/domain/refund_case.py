from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from .refund_request import RefundRequest, RefundRequestStatus
from .refund_response import RefundResponse, ResponseType, RefundMethod
from .value_objects.case_timeline import CaseTimeline


RefundStatus = RefundRequestStatus  # Alias for consistency


class RefundCase:
    """Aggregate root for refund workflow and state management
    
    This aggregate controls the complete refund workflow lifecycle,
    containing RefundRequest entities and managing business rules.
    """

    def __init__(
        self,
        refund_case_id: str,
        case_number: str,
        customer_id: str,
        order_id: str,
        refund_request: Optional[RefundRequest] = None,
        refund_responses: Optional[List[RefundResponse]] = None,
        timeline: Optional[List[CaseTimeline]] = None,
        status: RefundStatus = RefundStatus.PENDING,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.refund_case_id = refund_case_id
        self.case_number = case_number
        self.customer_id = customer_id
        self.order_id = order_id
        self.refund_request = refund_request
        self.refund_responses = refund_responses or []
        self.timeline = timeline or []
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def add_refund_request(
        self,
        product_ids: List[str],
        request_reason: str,
        evidence_photos: Optional[List[str]] = None,
        delivery_date: Optional[str] = None
    ) -> RefundRequest:
        """Create and add a refund request to this case"""
        from .refund_request import RefundRequest
        from .services.eligibility_service import EligibilityService
        
        if self.refund_request:
            raise ValueError("Refund case already has a refund request")
        
        refund_request = RefundRequest(
            refund_request_id=str(uuid4()),
            product_ids=product_ids,
            request_reason=request_reason,
            evidence_photos=evidence_photos or [],
            status=RefundRequestStatus.PENDING
        )
        
        # Check eligibility
        is_defective = "defect" in request_reason.lower() or "damage" in request_reason.lower()
        is_eligible_for_refund = EligibilityService.is_eligible_for_refund(
            refund_request, delivery_date or "", is_defective
        )
        
        refund_request.is_eligible_for_refund = is_eligible_for_refund
        
        self.refund_request = refund_request
        self.status = RefundStatus.PENDING
        self.updated_at = datetime.utcnow()
        
        # Add to timeline
        self.timeline.append(CaseTimeline(
            status="refund_request_submitted",
            actor=self.customer_id,
            notes="Customer submitted refund request"
        ))
        
        # Add eligibility status to timeline
        if not refund_request.is_eligible_for_refund:
            self.timeline.append(CaseTimeline(
                status="refund_request_not_eligible",
                actor="system",
                notes="Refund request not eligible based on business rules"
            ))
        
        return refund_request

    def add_refund_response(
        self,
        agent_id: str,
        response_type: ResponseType,
        response_content: str,
        refund_amount: Optional[str] = None,
        refund_method: Optional[RefundMethod] = None,
        attachments: Optional[List[str]] = None
    ) -> RefundResponse:
        """Add a response/decision to the refund case"""
        from .refund_response import RefundResponse
        
        if not self.refund_request:
            raise ValueError("Cannot add response to case without refund request")
        
        response = RefundResponse(
            response_id=str(uuid4()),
            refund_request_id=self.refund_request.refund_request_id,
            agent_id=agent_id,
            response_type=response_type,
            response_content=response_content,
            refund_amount=refund_amount,
            refund_method=refund_method,
            attachments=attachments or []
        )
        
        self.refund_responses.append(response)
        
        # Update status based on response type
        if response_type == ResponseType.APPROVAL:
            self.status = RefundStatus.APPROVED
            self.refund_request.approve(agent_id, response_content)
        elif response_type == ResponseType.REJECTION:
            self.status = RefundStatus.REJECTED
            self.refund_request.reject(agent_id, response_content)
        
        self.updated_at = datetime.utcnow()
        
        # Add to timeline
        status_verb = "approved" if response_type == "approval" else "rejected"
        self.timeline.append(CaseTimeline(
            status=f"refund_request_{status_verb}",
            actor=agent_id,
            notes=f"Agent {response_type} refund request"
        ))
        
        return response

    def can_process_refund(self) -> bool:
        """Check if refund can be processed based on business rules"""
        if not self.refund_request:
            return False
        
        # Check if at least one product is specified
        if not self.refund_request.product_ids:
            return False
        
        # Validate evidence
        if not self.refund_request.evidence_photos:
            return False
        
        return True

    # submit_feedback method removed

    def __str__(self) -> str:
        return f"RefundCase {self.refund_case_id} ({self.status.value})"

    def __repr__(self) -> str:
        return f"<RefundCase {self.refund_case_id} customer={self.customer_id} status={self.status.value}>"