"""UpdateCaseType use case implementation"""

from typing import Dict, Any, Optional
from domain.support_case import SupportCase, CaseType


class UpdateCaseType:
    """Use case for updating the type of a support case"""

    def __init__(self, support_case_repository):
        """Initialize with required dependencies"""
        self.support_case_repository = support_case_repository

    def execute(
        self,
        case_number: str,
        case_type: str,
        refund_request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute the update case type use case"""
        
        # Validate inputs
        if not case_number or not case_type:
            raise ValueError("Case number and case type are required")
        
        # Find support case
        support_case = self.support_case_repository.find_by_case_number(case_number)
        
        if not support_case:
            raise ValueError(f"Support case {case_number} not found")
        
        # Validate case type
        try:
            case_type_enum = CaseType(case_type.lower())
        except ValueError:
            raise ValueError(f"Invalid case type: {case_type}")
        
        # Update case type
        support_case.update_case_type(
            case_type=case_type_enum,
            refund_request_id=refund_request_id
        )
        
        # Save updated support case
        self.support_case_repository.save(support_case)
        
        return {
            "status": "case_type_updated",
            "support_case": support_case
        }