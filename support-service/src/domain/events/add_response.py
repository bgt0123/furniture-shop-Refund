"""AddResponse use case implementation"""

from typing import Dict, Any, Optional
from uuid import uuid4

from domain.support_case import SupportCase, SenderType, MessageType


class AddResponse:
    """Use case for adding a response to a support case"""

    def __init__(self, support_case_repository):
        """Initialize with required dependencies"""
        self.support_case_repository = support_case_repository

    def execute(
        self,
        case_number: str,
        sender_id: str,
        sender_type: str,
        content: str,
        message_type: str,
        attachments: Optional[list] = None,
        is_internal: bool = False
    ) -> Dict[str, Any]:
        """Execute the add response use case"""
        
        # Validate inputs
        if not case_number or not sender_id or not content:
            raise ValueError("Case number, sender ID, and content are required")
        
        # Find support case
        support_case = self.support_case_repository.find_by_case_number(case_number)
        
        if not support_case:
            raise ValueError(f"Support case {case_number} not found")
        
        # Validate sender type
        try:
            sender_type_enum = SenderType(sender_type.lower())
        except ValueError:
            raise ValueError(f"Invalid sender type: {sender_type}")
        
        # Validate message type
        try:
            message_type_enum = MessageType(message_type.lower())
        except ValueError:
            raise ValueError(f"Invalid message type: {message_type}")
        
        # Add response (this will validate if case is closed)
        response = support_case.add_response(
            sender_id=sender_id,
            sender_type=sender_type_enum,
            content=content,
            message_type=message_type_enum,
            attachments=attachments,
            is_internal=is_internal
        )
        
        # Save updated support case
        self.support_case_repository.save(support_case)
        
        return {
            "response_id": response.response_id,
            "case_number": case_number,
            "status": "response_added",
            "response": response,
            "support_case": support_case
        }