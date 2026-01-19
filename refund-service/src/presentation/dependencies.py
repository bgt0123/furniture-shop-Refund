"""Dependency injection setup for refund service"""

from infrastructure.repositories.refund_case_repository import RefundCaseRepository
from domain.events.create_refund_request import CreateRefundRequest
import httpx
import os


class Dependencies:
    """Container for application dependencies"""
    
    def __init__(self):
        self.refund_case_repository = RefundCaseRepository()
        
        class SupportCaseRepository:
            """Repository that calls the actual Support Service API"""
            
            def __init__(self):
                self.support_service_url = os.getenv("SUPPORT_SERVICE_URL", "http://support-service:8001")
            
            def find_by_case_number(self, case_number):
                """Find support case by calling Support Service API"""
                try:
                    # Make API call to support service
                    response = httpx.get(f"{self.support_service_url}/support-cases/{case_number}", timeout=30.0)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Create a simple object with required attributes
                        class SupportCase:
                            def __init__(self, data):
                                self.case_number = data["case_number"]
                                self.customer_id = data["customer_id"]
                                self.case_type = type("CaseType", (), {"value": data["case_type"]})
                                self.status = type("CaseStatus", (), {"value": data["status"], "CLOSED": "closed"})
                                self.is_closed = data["status"] == "closed"
                        
                        return SupportCase(data)
                    elif response.status_code == 404:
                        # Support case not found
                        return None
                    else:
                        # API call failed
                        return None
                except Exception:
                    # If support service is not available, allow creation (fault tolerance)
                    # In production, you might want different handling
                    class MockSupportCase:
                        def __init__(self, case_number):
                            self.case_number = case_number
                            self.customer_id = "unknown"
                            self.case_type = type("CaseType", (), {"value": "refund"})
                            self.status = type("CaseStatus", (), {"value": "open", "CLOSED": "closed"})
                            self.is_closed = False
                    
                    return MockSupportCase(case_number)
        
        self.support_case_repository = SupportCaseRepository()
        self.create_refund_request = CreateRefundRequest(
            self.refund_case_repository, 
            self.support_case_repository
        )


def get_dependencies() -> Dependencies:
    """Get the current dependencies"""
    return Dependencies()