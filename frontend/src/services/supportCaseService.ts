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

class SupportCaseService {
  async createSupportCase(request: CreateSupportCaseRequest): Promise<SupportCase> {
    try {
      const response = await apiClient.post('/api/support-cases', request)
      return response.data
    } catch (error) {
      throw new Error(`Failed to create support case: ${error}`)
    }
  }

  async getSupportCase(caseId: string): Promise<SupportCase> {
    try {
      const response = await apiClient.get(`/api/support-cases/${caseId}`)
      return response.data
    } catch (error) {
      throw new Error(`Failed to fetch support case: ${error}`)
    }
  }

  async updateSupportCaseStatus(
    caseId: string,
    status: UpdateSupportCaseStatusRequest
  ): Promise<SupportCase> {
    try {
      const response = await apiClient.patch(
        `/api/support-cases/${caseId}/status`,
        status
      )
      return response.data
    } catch (error) {
      throw new Error(`Failed to update support case status: ${error}`)
    }
  }

  async getMySupportCases(): Promise<SupportCase[]> {
    try {
      const response = await apiClient.get('/api/support-cases')
      return response.data
    } catch (error) {
      throw new Error(`Failed to fetch support cases: ${error}`)
    }
  }
}

export const supportCaseService = new SupportCaseService()