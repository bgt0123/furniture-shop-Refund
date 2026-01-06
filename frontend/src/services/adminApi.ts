import axios, { AxiosInstance, AxiosResponse } from 'axios'

class AdminApiClient {
  private instance: AxiosInstance
  
  constructor(baseURL: string, token?: string) {
    this.instance = axios.create({
      baseURL: `${baseURL}/admin`,
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    if (token) {
      this.setAuthToken(token)
    }
  }
  
  setAuthToken(token: string): void {
    this.instance.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }
  
  clearAuthToken(): void {
    delete this.instance.defaults.headers.common['Authorization']
  }
  
  async getAllRefundCases(token: string, params?: any): Promise<AxiosResponse> {
    return this.instance.get('/refunds/cases', { params })
  }
  
  async getRefundCaseDetails(token: string, refundId: string): Promise<AxiosResponse> {
    return this.instance.get(`/refunds/cases/${refundId}`)
  }
  
  async approveRefund(token: string, refundId: string): Promise<AxiosResponse> {
    return this.instance.post(`/refunds/cases/${refundId}/approve`)
  }
  
  async rejectRefund(token: string, refundId: string, reason: string): Promise<AxiosResponse> {
    return this.instance.post(`/refunds/cases/${refundId}/reject`, { reason })
  }
}

export const adminApi = new AdminApiClient('/api/v1')