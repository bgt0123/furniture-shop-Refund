"""DeleteCase use case implementation"""

from typing import Dict, Any
from domain.support_case import SupportCase


class DeleteCase:
    """Use case for deleting a support case"""

    def __init__(self, support_case_repository):
        """Initialize with required dependencies"""
        self.support_case_repository = support_case_repository

    def execute(self, case_number: str) -> Dict[str, Any]:
        """Execute the delete support case use case"""
        
        # Find the support case
        support_case = self.support_case_repository.find_by_case_number(case_number)
        if not support_case:
            raise ValueError(f"Support case {case_number} not found")
        
        # Check if case can be deleted
        if support_case.refund_request_ids and len(support_case.refund_request_ids) > 0:
            raise ValueError("Cannot delete support case with active refund requests")
        
        # Mark case as deleted
        support_case.delete_case()
        
        # Save the updated case
        self.support_case_repository.save(support_case)
        
        return {
            "support_case": support_case
        }