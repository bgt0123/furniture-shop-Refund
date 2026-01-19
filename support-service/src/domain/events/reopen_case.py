"""ReopenCase use case implementation"""

from typing import Dict, Any
from domain.support_case import SupportCase


class ReopenCase:
    """Use case for reopening a support case"""

    def __init__(self, support_case_repository):
        """Initialize with required dependencies"""
        self.support_case_repository = support_case_repository

    def execute(
        self,
        case_number: str
    ) -> Dict[str, Any]:
        """Execute the reopen case use case"""
        
        # Validate inputs
        if not case_number:
            raise ValueError("Case number is required")
        
        # Find support case
        support_case = self.support_case_repository.find_by_case_number(case_number)
        
        if not support_case:
            raise ValueError(f"Support case {case_number} not found")
        
        # Reopen the case
        support_case.reopen_case()
        
        # Save updated support case
        self.support_case_repository.save(support_case)
        
        return {
            "status": "case_reopened",
            "support_case": support_case
        }