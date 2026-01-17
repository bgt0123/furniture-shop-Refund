import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

interface RefundCase {
  refund_id: string;
  support_case_id: string;
  status: 'pending' | 'approved' | 'executed' | 'failed' | 'cancelled';
  requested_amount: number;
  approved_amount?: number;
  delivery_date: string;
  refund_requested_at: string;
}

export const refundCaseService = {
  async getPendingRefunds(): Promise<RefundCase[]> {
    const token = localStorage.getItem('auth_token');
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
    try {
      const response = await axios.get(`${API_BASE_URL}/refund-cases/`, config);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch pending refunds:', error);
      return [];
    }
  },

  async approveRefund(refundId: string, amount?: number): Promise<RefundCase> {
    const token = localStorage.getItem('auth_token');
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
    const requestBody = amount !== undefined ? { approved_amount: amount } : {};
    
    try {
      const response = await axios.put(
        `${API_BASE_URL}/refund-cases/${refundId}/approve`,
        requestBody,
        config
      );
      return response.data;
    } catch (error) {
      console.error('Failed to approve refund:', error);
      throw error;
    }
  },

  async executeRefund(refundId: string): Promise<RefundCase> {
    // In a real implementation, this would require authentication
    try {
      const response = await axios.post(
        `${API_BASE_URL}/refund-cases/${refundId}/execute`
      );
      return response.data;
    } catch (error) {
      console.error('Failed to execute refund:', error);
      throw error;
    }
  },

  async cancelRefund(refundId: string): Promise<RefundCase> {
    // In a real implementation, this would require authentication
    try {
      const response = await axios.post(
        `${API_BASE_URL}/refund-cases/${refundId}/cancel`
      );
      return response.data;
    } catch (error) {
      console.error('Failed to cancel refund:', error);
      throw error;
    }
  }
};