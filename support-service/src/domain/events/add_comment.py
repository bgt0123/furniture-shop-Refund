"""AddComment use case implementation"""

from typing import Dict, Any, List, Optional
from domain.support_case import SupportCase
from domain.comment import CommentType


class AddComment:
    """Use case for adding a comment to a support case"""

    def __init__(self, support_case_repository):
        """Initialize with required dependencies"""
        self.support_case_repository = support_case_repository

    def execute(
        self,
        case_number: str,
        author_id: str,
        author_type: str,
        content: str,
        comment_type: str,
        attachments: Optional[List[str]] = None,
        is_internal: bool = False
    ) -> Dict[str, Any]:
        """Execute the add comment use case"""
        
        # Validate inputs
        if not author_id or not content:
            raise ValueError("Author ID and content are required")
        
        # Validate author type
        if author_type not in ["customer", "agent", "refund_service"]:
            raise ValueError(f"Invalid author type: {author_type}")
        
        # Validate comment type
        try:
            comment_type_enum = CommentType(comment_type)
        except ValueError:
            raise ValueError(f"Invalid comment type: {comment_type}")
        
        # Find support case
        support_case = self.support_case_repository.find_by_case_number(case_number)
        if not support_case:
            raise ValueError(f"Support case {case_number} not found")
        
        # Add comment
        print(f"DEBUG: Before adding comment, case has {len(support_case.comments) if support_case.comments else 0} comments")
        comment = support_case.add_comment(
            author_id=author_id,
            author_type=author_type,
            content=content,
            comment_type=comment_type_enum,
            attachments=attachments if attachments is not None else [],
            is_internal=is_internal
        )
        print(f"DEBUG: After adding comment, case has {len(support_case.comments) if support_case.comments else 0} comments")
        
        # Save to repository
        self.support_case_repository.save(support_case)
        
        return {
            "status": "comment_added",
            "comment": comment,
            "support_case": support_case
        }