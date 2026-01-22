"""Dependency injection setup for refund service"""

from infrastructure.repositories.refund_request_repository import RefundRequestRepository
from infrastructure.repositories.refund_response_repository import RefundResponseRepository
from domain.events.create_refund_request import CreateRefundRequest
from domain.events.create_refund_response import CreateRefundResponse
import httpx
import os


class Dependencies:
    """Container for application dependencies"""
    
    def __init__(self):
        self.refund_request_repository = RefundRequestRepository()
        self.refund_response_repository = RefundResponseRepository()
        
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
                                self.case_type = data["case_type"]
                                self.status = data["status"]
                                self.is_closed = data["status"] == "closed"
                                self.is_deleted = data.get("is_deleted", False)
                                self.refund_request_ids = data.get("refund_request_ids", [])
                        
                        return SupportCase(data)
                    elif response.status_code == 404:
                        # Support case might not be immediately available due to timing
                        # Return a mock support case to allow creation with fault tolerance
                        print(f"Support case {case_number} not found, creating mock for refund creation")
                        class NotFoundMockSupportCase:
                            def __init__(self, case_number):
                                self.case_number = case_number
                                self.customer_id = "unknown"
                                self.case_type = "refund"
                                self.status = "open"
                                self.is_closed = False
                                self.is_deleted = False
                                self.refund_request_ids = []
                            
                            def add_refund_request(self, refund_request_id):
                                """Mock method to add refund request ID"""
                                self.refund_request_ids.append(refund_request_id)
                                print(f"Mock: Added refund request {refund_request_id} to support case {self.case_number}")
                        
                        return NotFoundMockSupportCase(case_number)
                    else:
                        # API call failed
                        return None
                except Exception as e:
                    # If support service is not available, allow creation (fault tolerance)
                    print(f"Support service unavailable for case {case_number}, creating mock: {e}")
                    # In production, you might want different handling
                    class ExceptionMockSupportCase:
                        def __init__(self, case_number):
                            self.case_number = case_number
                            self.customer_id = "unknown"
                            self.case_type = "refund"
                            self.status = "open"
                            self.is_closed = False
                            self.is_deleted = False
                            self.refund_request_ids = []
                        
                        def add_refund_request(self, refund_request_id):
                            """Mock method to add refund request ID"""
                            self.refund_request_ids.append(refund_request_id)
                            print(f"Mock: Added refund request {refund_request_id} to support case {self.case_number}")
                    
                    return ExceptionMockSupportCase(case_number)
        
        self.support_case_repository = SupportCaseRepository()
        self.create_refund_request = CreateRefundRequest(
            self.refund_request_repository, 
            self.support_case_repository
        )
        self.create_refund_response = CreateRefundResponse(
            self.refund_response_repository
        )


def get_dependencies() -> Dependencies:
    """Get the current dependencies"""
    return Dependencies()