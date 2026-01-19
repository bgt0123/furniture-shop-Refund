"""CloseCase use case implementation"""

from typing import Dict, Any
from ..support_case import SupportCase


class CloseCase:
    """Use case for closing a support case"""

    def __init__(self, support_case_repository):
        """Initialize with required dependencies"""
        self.support_case_repository = support_case_repository

    def execute(
        self,
        case_number: str
    ) -> Dict[str, Any]:
        """Execute the close case use case"""
        
        # Validate inputs
        if not case_number:
            raise ValueError("Case number is required")
        
        # Find support case
        support_case = self.support_case_repository.find_by_case_number(case_number)
        
        if not support_case:
            raise ValueError(f"Support case {case_number} not found")
        
        # Close case
        support_case.close_case()
        
        # Save updated support case
        self.support_case_repository.save(support_case)
        
        return {
            "case_number": case_number,
            "status": "case_closed",
            "support_case": support_case
        }