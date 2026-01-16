import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API service methods
export const apiService = {
  // Health check
  healthCheck: () => apiClient.get('/health'),

  // Support cases
  createSupportCase: (data: any) => apiClient.post('/support/cases', data),
  getSupportCase: (caseId: string) => apiClient.get(`/support/cases/${caseId}`),
  getCustomerSupportCases: (customerId: string) => 
    apiClient.get(`/support/cases/customer/${customerId}`),
  closeSupportCase: (caseId: string) => 
    apiClient.patch(`/support/cases/${caseId}/close`),

  // Authentication helpers
  setAuthToken: (token: string) => {
    localStorage.setItem('auth_token', token);
  },
  
  getAuthToken: () => {
    return localStorage.getItem('auth_token');
  },

  clearAuth: () => {
    localStorage.removeItem('auth_token');
  }
};

export default apiService;