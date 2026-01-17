import axios from 'axios'

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

export type SupportCase = {
  case_id: string
  customer_id: string
  order_id: string
  title: string
  description: string
  status: 'open' | 'in_progress' | 'resolved' | 'closed'
  created_at: string
  updated_at: string
}

export type CreateSupportCaseRequest = {
  title: string
  description: string
  orderId: string
}

export type UpdateSupportCaseStatusRequest = {
  status: 'open' | 'in_progress' | 'resolved' | 'closed'
}

// Helper function to get or create authentication token
async function ensureAuthenticated(): Promise<void> {
  if (!localStorage.getItem('auth_token')) {
    try {
      const response = await apiClient.post('/auth/test-login');
      localStorage.setItem('auth_token', response.data.access_token);
    } catch (error) {
      throw new Error('Failed to authenticate: ' + error);
    }
  }
}

class SupportCaseService {
  async createSupportCase(request: CreateSupportCaseRequest): Promise<SupportCase> {
    await ensureAuthenticated();
    try {
      // Convert camelCase to snake_case for backend
      const backendRequest = {
        title: request.title,
        description: request.description,
        order_id: request.orderId  // Convert orderId to order_id
      }
      const response = await apiClient.post('/support-cases', backendRequest)
      return response.data
    } catch (error) {
      throw new Error(`Failed to create support case: ${error}`)
    }
  }

  async getSupportCase(caseId: string): Promise<SupportCase> {
    await ensureAuthenticated();
    try {
      const response = await apiClient.get(`/support-cases/${caseId}`)
      return response.data
    } catch (error) {
      throw new Error(`Failed to fetch support case: ${error}`)
    }
  }

  async updateSupportCaseStatus(
    caseId: string,
    status: UpdateSupportCaseStatusRequest
  ): Promise<SupportCase> {
    await ensureAuthenticated();
    try {
      const response = await apiClient.patch(
        `/support-cases/${caseId}/status`,
        status
      )
      return response.data
    } catch (error) {
      throw new Error(`Failed to update support case status: ${error}`)
    }
  }

  async getMySupportCases(): Promise<SupportCase[]> {
    await ensureAuthenticated();
    try {
      const response = await apiClient.get('/support-cases')
      return response.data
    } catch (error) {
      throw new Error(`Failed to fetch support cases: ${error}`)
    }
  }
}

export const supportCaseService = new SupportCaseService()