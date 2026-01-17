import axios from 'axios';
import { RefundCaseApproval, RefundCaseRejection } from '../types/models';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Create separate axios instance for agent operations
const agentApiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Agent-specific request interceptor
agentApiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('agent_auth_token');
    const agentId = localStorage.getItem('agent_id');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    if (agentId) {
      config.headers['X-Agent-ID'] = agentId;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for agent operations
agentApiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized agent - redirect to agent login
      localStorage.removeItem('agent_auth_token');
      localStorage.removeItem('agent_id');
      window.location.href = '/agent-login';
    }
    return Promise.reject(error);
  }
);

// Agent-specific API service methods
export const agentApiService = {
  // Agent authentication
  loginAgent: (email: string, password: string) => 
    agentApiClient.post('/agent/login', { email, password }),

  // Get agent details
  getAgentProfile: () => agentApiClient.get('/agent/profile'),

  // Refund case operations
  getAdminRefundCases: (params?: { 
    status?: string; 
    customerId?: string; 
    limit?: number; 
    offset?: number 
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append('status', params.status);
    if (params?.customerId) queryParams.append('customerId', params.customerId);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());
    
    const queryString = queryParams.toString();
    return agentApiClient.get(`/admin/refunds/cases${queryString ? `?${queryString}` : ''}`);
  },

  getAdminRefundCase: (refundId: string) => 
    agentApiClient.get(`/admin/refunds/cases/${refundId}`),

  approveRefundCase: (refundId: string, approvalData?: RefundCaseApproval) => 
    agentApiClient.post(`/admin/refunds/cases/${refundId}/approve`, approvalData || {}),

  rejectRefundCase: (refundId: string, rejectionData: RefundCaseRejection) => 
    agentApiClient.post(`/admin/refunds/cases/${refundId}/reject`, rejectionData),

  getPendingRefundCases: (limit?: number, offset?: number) => {
    const queryParams = new URLSearchParams();
    if (limit) queryParams.append('limit', limit.toString());
    if (offset) queryParams.append('offset', offset.toString());
    
    const queryString = queryParams.toString();
    return agentApiClient.get(`/admin/refunds/cases/pending${queryString ? `?${queryString}` : ''}`);
  },

  // Agent authentication helpers
  setAgentAuth: (token: string, agentId: string) => {
    localStorage.setItem('agent_auth_token', token);
    localStorage.setItem('agent_id', agentId);
  },

  getAgentAuthToken: () => {
    return localStorage.getItem('agent_auth_token');
  },

  getAgentId: () => {
    return localStorage.getItem('agent_id');
  },

  clearAgentAuth: () => {
    localStorage.removeItem('agent_auth_token');
    localStorage.removeItem('agent_id');
  },

  isAgentAuthenticated: () => {
    return !!localStorage.getItem('agent_auth_token');
  }
};

export default agentApiService;