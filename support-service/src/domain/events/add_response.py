"""AddResponse event for handling agent responses to support cases"""

from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from ..support_case import SupportCase
from ..comment import Comment, CommentType


class AddResponse:
    """Event for adding an agent response to a support case"""
    
    def __init__(self, support_case_repository):
        self.support_case_repository = support_case_repository
    
    def execute(
        self,
        case_number: str,
        agent_id: str,
        content: str,
        attachments: Optional[List[str]] = None,
        is_internal: bool = False
    ) -> SupportCase:
        """Execute the add response event
        
        Args:
            case_number: The support case number
            agent_id: ID of the agent adding the response
            content: Content of the response
            attachments: Optional list of attachment URLs/paths
            is_internal: Whether this response is internal only
            
        Returns:
            Updated SupportCase
        """
        support_case = self.support_case_repository.find_by_case_number(case_number)
        
        if not support_case:
            raise ValueError(f"Support case {case_number} not found")
        
        # Add the agent response
        response = support_case.add_agent_response(
            agent_id=agent_id,
            content=content,
            attachments=attachments,
            is_internal=is_internal
        )
        
        # Save the updated support case
        self.support_case_repository.save(support_case)
        
        # Emit event if needed (for async processing)
        # self._emit_response_added_event(support_case, response)
        
        return support_case
    
    def _emit_response_added_event(self, support_case: SupportCase, response: Comment):
        """Emit event for async processing (if needed)"""
        # Placeholder for event emission
        pass