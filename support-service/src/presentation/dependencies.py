"""Dependency injection setup for support service"""

from infrastructure.repositories.support_case_repository import SupportCaseRepository
from domain.events.create_support_case import CreateSupportCase
from domain.events.add_response import AddResponse
from domain.events.assign_agent import AssignAgent
from domain.events.close_case import CloseCase
from domain.events.update_case_type import UpdateCaseType
from domain.events.add_comment import AddComment
from domain.events.delete_case import DeleteCase


class Dependencies:
    """Container for application dependencies"""
    
    def __init__(self):
        self.support_case_repository = SupportCaseRepository()
        self.create_support_case = CreateSupportCase(self.support_case_repository)
        self.add_response = AddResponse(self.support_case_repository)
        self.add_comment = AddComment(self.support_case_repository)
        self.assign_agent = AssignAgent(self.support_case_repository)
        self.close_case = CloseCase(self.support_case_repository)
        self.update_case_type = UpdateCaseType(self.support_case_repository)
        self.delete_case = DeleteCase(self.support_case_repository)


def get_dependencies() -> Dependencies:
    """Get the current dependencies"""
    return Dependencies()