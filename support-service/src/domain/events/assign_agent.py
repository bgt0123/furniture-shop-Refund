"""AssignAgent use case implementation"""

from typing import Dict, Any
from ..support_case import SupportCase


class AssignAgent:
    """Use case for assigning an agent to a support case"""

    def __init__(self, support_case_repository):
        """Initialize with required dependencies"""
        self.support_case_repository = support_case_repository

    def execute(
        self,
        case_number: str,
        agent_id: str
    ) -> Dict[str, Any]:
        """Execute the assign agent use case"""
        
        # Validate inputs
        if not case_number or not agent_id:
            raise ValueError("Case number and agent ID are required")
        
        # Find support case
        support_case = self.support_case_repository.find_by_case_number(case_number)
        
        if not support_case:
            raise ValueError(f"Support case {case_number} not found")
        
        # Assign agent (this will validate if case is closed)
        support_case.assign_agent(agent_id)
        
        # Save updated support case
        self.support_case_repository.save(support_case)
        
        return {
            "case_number": case_number,
            "agent_id": agent_id,
            "status": "agent_assigned",
            "support_case": support_case
        }