// API service for communicating with backend services

// Use relative paths for proxy in development, absolute URLs for production
// Use Docker service names when running in container, localhost when running locally
const SUPPORT_SERVICE_BASE_URL = 
  window.location.hostname === 'localhost' 
    ? 'http://localhost:8001' 
    : 'http://support-service:8001';

const REFUND_SERVICE_BASE_URL = 
  window.location.hostname === 'localhost' 
    ? 'http://localhost:8002' 
    : 'http://refund-service:8002';

interface SupportCase {
  case_number: string;
  customer_id: string;
  case_type: string;
  subject: string;
  description: string;
  status: string;
  refund_request_id?: string;
  assigned_agent_id?: string;
  created_at: string;
  updated_at: string;
}

interface DetailedSupportCase extends SupportCase {
  responses?: SupportResponse[];
  attachments?: string[];
}

interface SupportResponse {
  id: string;
  sender_id: string;
  sender_type: string;
  content: string;
  message_type: string;
  attachments?: string[];
  is_internal?: boolean;
  created_at: string;
}

interface CreateSupportCaseRequest {
  customer_id: string;
  case_type: string;
  subject: string;
  description: string;
  refund_request_id?: string;
  evidence_files?: string[];
}

interface SupportResponseRequest {
  sender_id: string;
  sender_type: string;
  content: string;
  message_type: string;
  attachments?: string[];
  is_internal?: boolean;
}

interface CreateRefundRequest {
  case_number: string;
  customer_id: string;
  order_id: string;
  product_ids: string[];
  request_reason: string;
  evidence_photos?: string[];
}

interface RefundCaseResponse {
  refund_case_id: string;
  case_number: string;
  customer_id: string;
  order_id: string;
  status: string;
  created_at: string;
  updated_at: string;
}

interface DetailedRefundCase extends RefundCaseResponse {
  request_reason: string;
  product_ids: string[];
  evidence_photos?: string[];
  support_case_details?: SupportCase;
}

class ApiError extends Error {
  constructor(message: string, public statusCode?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

async function apiCall(url: string, options: RequestInit = {}) {
  try {
    const fullUrl = url.startsWith('http') ? url : url;
    const response = await fetch(fullUrl, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.text().catch(() => null);
      
      // Try to parse as JSON, but handle HTML responses gracefully
      let errorMessage = `HTTP error! status: ${response.status}`;
      if (errorData) {
        try {
          const parsed = JSON.parse(errorData);
          errorMessage = parsed?.detail || errorMessage;
        } catch {
          // If parsing fails (e.g., HTML content), use the status text
          errorMessage = response.statusText || errorMessage;
        }
      }
      
      throw new ApiError(errorMessage, response.status);
    }

    return await response.json();
    } catch (error: any) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Handle network errors
      if (error.message && error.message.includes('Failed to fetch')) {
        throw new ApiError('Backend service is not available. Please make sure the server is running.', 0);
      }
      
      throw new ApiError(`Network error: ${error.message}`);
    }
}

// Support Case API

export const supportApi = {
  async createSupportCase(data: CreateSupportCaseRequest): Promise<SupportCase> {
    return apiCall(`${SUPPORT_SERVICE_BASE_URL}/support-cases`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getSupportCase(caseNumber: string): Promise<SupportCase> {
    return apiCall(`${SUPPORT_SERVICE_BASE_URL}/support-cases/${caseNumber}`);
  },

  async getSupportCaseDetailed(caseNumber: string): Promise<DetailedSupportCase> {
    return apiCall(`${SUPPORT_SERVICE_BASE_URL}/support-cases/${caseNumber}/detailed`).catch(() => {
      // Fallback to basic case info if detailed endpoint doesn't exist
      return this.getSupportCase(caseNumber).then(caseData => ({
        ...caseData,
        responses: [],
        attachments: []
      }));
    });
  },

  async getCustomerSupportCases(customerId: string): Promise<SupportCase[]> {
    return apiCall(`${SUPPORT_SERVICE_BASE_URL}/support-cases/customer/${customerId}`);
  },

  async addResponse(caseNumber: string, data: SupportResponseRequest) {
    return apiCall(`${SUPPORT_SERVICE_BASE_URL}/support-cases/${caseNumber}/responses`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async assignAgent(caseNumber: string, agentId: string): Promise<SupportCase> {
    return apiCall(`${SUPPORT_SERVICE_BASE_URL}/support-cases/${caseNumber}/assign/${agentId}`, {
      method: 'PUT',
    });
  },

  async closeCase(caseNumber: string): Promise<SupportCase> {
    return apiCall(`${SUPPORT_SERVICE_BASE_URL}/support-cases/${caseNumber}/close`, {
      method: 'PUT',
    });
  },

  async reopenCase(caseNumber: string): Promise<SupportCase> {
    return apiCall(`${SUPPORT_SERVICE_BASE_URL}/support-cases/${caseNumber}/reopen`, {
      method: 'PUT',
    });
  },

  async updateCaseType(caseNumber: string, caseType: string, refundRequestId?: string): Promise<SupportCase> {
    return apiCall(`${SUPPORT_SERVICE_BASE_URL}/support-cases/${caseNumber}/update-type`, {
      method: 'PUT',
      body: JSON.stringify({
        case_type: caseType,
        refund_request_id: refundRequestId
      }),
    });
  },

  async uploadEvidence(caseNumber: string, files: File[]) {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    return apiCall(`${SUPPORT_SERVICE_BASE_URL}/support-cases/${caseNumber}/upload-evidence`, {
      method: 'POST',
      body: formData,
      headers: {
        // Remove Content-Type header for FormData
      },
    });
  },
};

// Refund Case API

export const refundApi = {
  // Create a new refund request
  async createRefundRequest(data: CreateRefundRequest): Promise<RefundCaseResponse> {
    return apiCall(`${REFUND_SERVICE_BASE_URL}/refund-cases`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Get a refund case by ID
  async getRefundCase(refundCaseId: string): Promise<RefundCaseResponse> {
    return apiCall(`${REFUND_SERVICE_BASE_URL}/refund-cases/${refundCaseId}`);
  },

  // Get a refund case with detailed information
  async getRefundCaseDetailed(refundCaseId: string): Promise<DetailedRefundCase> {
    return apiCall(`${REFUND_SERVICE_BASE_URL}/refund-cases/${refundCaseId}/detailed`).catch(() => {
      // Fallback to basic case info if detailed endpoint doesn't exist
      return this.getRefundCase(refundCaseId).then(caseData => ({
        ...caseData,
        request_reason: 'Refund request',
        product_ids: [],
        evidence_photos: [],
        support_case_details: undefined
      }));
    });
  },

  // Get refund cases for a customer (to be implemented in backend)
  async getCustomerRefundCases(customerId: string): Promise<RefundCaseResponse[]> {
    // This endpoint doesn't exist yet in the backend
    return apiCall(`${REFUND_SERVICE_BASE_URL}/refund-cases/customer/${customerId}`).catch(() => {
      // Return empty array if endpoint doesn't exist
      return [];
    });
  },

  // Upload evidence for refund
  async uploadRefundEvidence(refundCaseId: string, files: File[]) {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    return apiCall(`${REFUND_SERVICE_BASE_URL}/refund-cases/${refundCaseId}/upload-evidence`, {
      method: 'POST',
      body: formData,
      headers: {
        // Remove Content-Type header for FormData
      },
    });
  },
};

export { ApiError };