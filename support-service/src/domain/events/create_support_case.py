"""CreateSupportCase use case implementation"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4

from domain.support_case import SupportCase, CaseType, CaseStatus


class CreateSupportCase:
    """Use case for creating a new support case"""

    def __init__(self, support_case_repository):
        """Initialize with required dependencies"""
        self.support_case_repository = support_case_repository

    def execute(
        self,
        customer_id: str,
        case_type: str,
        subject: str,
        description: str,
        refund_request_id: Optional[str] = None,
        order_id: Optional[str] = None,
        product_ids: Optional[List[str]] = None,
        delivery_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute the create support case use case"""
        
        # Validate inputs
        if not customer_id or not subject or not description:
            raise ValueError("Customer ID, subject, and description are required")
        
        # Validate case type
        try:
            case_type_enum = CaseType(case_type.lower())
        except ValueError:
            raise ValueError(f"Invalid case type: {case_type}. Must be 'question' or 'refund'")
        
        # Generate case number
        case_number = f"SC-{uuid4().hex[:8].upper()}"
        
        # Parse delivery date if provided
        parsed_delivery_date = None
        if delivery_date:
            try:
                parsed_delivery_date = datetime.fromisoformat(delivery_date)
            except ValueError:
                raise ValueError("Invalid delivery_date format. Must be ISO format")
        
        # Validate refund-specific fields
        if case_type_enum == CaseType.REFUND:
            if not order_id:
                raise ValueError("Order ID is required for refund cases")
            if not product_ids:
                raise ValueError("Product IDs are required for refund cases")
        
        # Create SupportCase aggregate
        support_case = SupportCase(
            case_number=case_number,
            customer_id=customer_id,
            case_type=case_type_enum,
            subject=subject,
            description=description,
            refund_request_id=refund_request_id,
            order_id=order_id,
            product_ids=product_ids or [],
            delivery_date=parsed_delivery_date,
            status=CaseStatus.OPEN
        )
        
        # Save to repository
        self.support_case_repository.save(support_case)
        
        return {
            "case_number": case_number,
            "status": "created",
            "support_case": support_case
        }