import React, { useState, useEffect } from 'react';
import { Card, Button } from '../components';
import { apiService } from '../services/api';

interface RefundCase {
  id: string;
  support_case_id: string;
  customer_id: string;
  order_id: string;
  products: Array<{
    id: string;
    name: string;
    price: number;
    quantity: number;
  }>;
  total_refund_amount: number;
  status: 'Pending' | 'Approved' | 'Rejected' | 'Completed';
  eligibility_status: 'Eligible' | 'Partially Eligible' | 'Ineligible';
  created_at: string;
  processed_at?: string;
  rejection_reason?: string;
  agent_id?: string;
}

interface RefundCaseListProps {
  customerId: string;
  onRefundSelect?: (refundId: string) => void;
}

export const RefundCaseList: React.FC<RefundCaseListProps> = ({ customerId, onRefundSelect }) => {
  const [refundCases, setRefundCases] = useState<RefundCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');

  useEffect(() => {
    loadRefundCases();
  }, [customerId]);

  const loadRefundCases = async () => {
    try {
      setLoading(true);
      let response;

      if (statusFilter) {
        // Use the new filtering endpoint
        response = await apiService.getRefundCases({
          customerId: customerId,
          status: statusFilter
        });
      } else {
        // Use customer-specific endpoint
        response = await apiService.getCustomerRefundCases(customerId);
      }

      setRefundCases(response.data);
    } catch (err: any) {
      setError('Failed to load refund cases');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'Pending': return 'status-pending';
      case 'Approved': return 'status-approved';
      case 'Rejected': return 'status-rejected';
      case 'Completed': return 'status-completed';
      default: return 'status-default';
    }
  };

  const getEligibilityBadgeClass = (eligibilityStatus: string) => {
    switch (eligibilityStatus) {
      case 'Eligible': return 'eligibility-eligible';
      case 'Partially Eligible': return 'eligibility-partial';
      case 'Ineligible': return 'eligibility-ineligible';
      default: return 'eligibility-default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <Card className="refund-case-list">
        <div className="loading">Loading refund cases...</div>
      </Card>
    );
  }

  return (
    <Card className="refund-case-list">
      <div className="refund-list-header">
        <h3>Refund Cases</h3>
        <div className="filters">
          <label>
            Filter by status:
            <select 
              value={statusFilter} 
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="Pending">Pending</option>
              <option value="Approved">Approved</option>
              <option value="Rejected">Rejected</option>
              <option value="Completed">Completed</option>
            </select>
          </label>
          <Button onClick={loadRefundCases}>Refresh</Button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {refundCases.length === 0 ? (
        <div className="empty-state">
          <p>No refund cases found</p>
        </div>
      ) : (
        <div className="refund-cases">
          {refundCases.map((refundCase) => (
            <div key={refundCase.id} className="refund-case-item" onClick={() => onRefundSelect?.(refundCase.id)}>
              <div className="refund-header">
                <div className="refund-info">
                  <h4>Refund #{refundCase.id.slice(0, 8)}...</h4>
                  <span className="order-id">Order #{refundCase.order_id}</span>
                </div>
                <div className="status-badges">
                  <span className={`status-badge ${getStatusBadgeClass(refundCase.status)}`}>
                    {refundCase.status}
                  </span>
                  <span className={`eligibility-badge ${getEligibilityBadgeClass(refundCase.eligibility_status)}`}>
                    {refundCase.eligibility_status}
                  </span>
                </div>
              </div>

              <div className="refund-details">
                <div className="products">
                  <strong>Products:</strong>
                  <ul>
                    {refundCase.products.map((product) => (
                      <li key={product.id}>
                        {product.name} - ${product.price} x {product.quantity}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="financial-info">
                  <div className="amount">
                    <strong>Total Refund:</strong> ${refundCase.total_refund_amount.toFixed(2)}
                  </div>
                  <div className="dates">
                    <span><strong>Created:</strong> {formatDate(refundCase.created_at)}</span>
                    {refundCase.processed_at && (
                      <span><strong>Processed:</strong> {formatDate(refundCase.processed_at)}</span>
                    )}
                  </div>
                </div>

                {refundCase.rejection_reason && (
                  <div className="rejection-reason">
                    <strong>Rejection Reason:</strong> {refundCase.rejection_reason}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};