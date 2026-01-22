// API client for communicating with backend services

const REFUND_SERVICE_BASE_URL = 'http://localhost:8002';
const SUPPORT_SERVICE_BASE_URL = 'http://localhost:8001';

export interface RequestInit {
  method?: string;
  headers?: Record<string, string>;
  body?: string;
}

export class ApiError extends Error {
  public statusCode?: number;
  
  constructor(message: string, status?: number) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = status;
  }
}

async function makeRequest(url: string, options: RequestInit = {}) {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  });

  if (!response.ok) {
    let errorMessage = response.statusText;
    
    // Try to get detailed error message from response body
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMessage = errorData.detail;
      }
    } catch {
      // If we can't parse JSON, use the status text
    }
    
    throw new ApiError(
      errorMessage,
      response.status
    );
  }

  return response.json();
}

// Refund Service API
export const refundApi = {
  getCustomerRefundCases: async (customerId: string) => {
    return makeRequest(`${REFUND_SERVICE_BASE_URL}/refund-cases/customer/${customerId}`);
  },

  makeRefundDecision: async (caseId: string, decisionData: any) => {
    return makeRequest(`${REFUND_SERVICE_BASE_URL}/refund-cases/${caseId}/decisions`, {
      method: 'POST',
      body: JSON.stringify(decisionData)
    });
  },

  createRefundRequest: async (refundData: any) => {
    return makeRequest(`${REFUND_SERVICE_BASE_URL}/refund-cases/`, {
      method: 'POST',
      body: JSON.stringify(refundData)
    });
  },

  getRefundCase: async (caseId: string) => {
    return makeRequest(`${REFUND_SERVICE_BASE_URL}/refund-cases/${caseId}`);
  },

  getAllRefundCases: async () => {
    return makeRequest(`${REFUND_SERVICE_BASE_URL}/refund-cases/`);
  },

  getRefundCaseDetailed: async (caseId: string) => {
    return makeRequest(`${REFUND_SERVICE_BASE_URL}/refund-cases/${caseId}/detailed`);
  }
};

// Support Service API
export const supportApi = {
  getSupportCase: async (caseNumber: string) => {
    return makeRequest(`${SUPPORT_SERVICE_BASE_URL}/support-cases/${caseNumber}`);
  },

  getCustomerSupportCases: async (customerId: string) => {
    return makeRequest(`${SUPPORT_SERVICE_BASE_URL}/support-cases/customer/${customerId}`);
  },

  createSupportCase: async (caseData: any) => {
    return makeRequest(`${SUPPORT_SERVICE_BASE_URL}/support-cases/`, {
      method: 'POST',
      body: JSON.stringify(caseData)
    });
  },

  updateCase: async (caseId: string, caseData: any) => {
    return makeRequest(`${SUPPORT_SERVICE_BASE_URL}/support-cases/${caseId}`, {
      method: 'PUT',
      body: JSON.stringify(caseData)
    });
  },

  updateCaseType: async (caseId: string, caseData: any) => {
    return makeRequest(`${SUPPORT_SERVICE_BASE_URL}/support-cases/${caseId}/type`, {
      method: 'PUT',
      body: JSON.stringify(caseData)
    });
  },

  closeCase: async (caseId: string) => {
    return makeRequest(`${SUPPORT_SERVICE_BASE_URL}/support-cases/${caseId}/close`, {
      method: 'PUT'
    });
  },



  addResponse: async (caseId: string, responseData: any) => {
    return makeRequest(`${SUPPORT_SERVICE_BASE_URL}/support-cases/${caseId}/responses`, {
      method: 'POST',
      body: JSON.stringify(responseData)
    });
  },

  getSupportCaseDetailed: async (caseNumber: string) => {
    return makeRequest(`${SUPPORT_SERVICE_BASE_URL}/support-cases/${caseNumber}`);
  },

  getAllSupportCases: async () => {
    return makeRequest(`${SUPPORT_SERVICE_BASE_URL}/support-cases/`);
  },

  addComment: async (caseNumber: string, commentData: any) => {
    return makeRequest(`${SUPPORT_SERVICE_BASE_URL}/support-cases/${caseNumber}/comments`, {
      method: 'POST',
      body: JSON.stringify(commentData)
    });
  }
};

// Feedback interface removed