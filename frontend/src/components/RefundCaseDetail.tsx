import React, { useState, useEffect } from 'react';
import { Card, Button } from '../components';
import { apiService } from '../services/api';

interface RefundCaseDetailProps {
  refundId: string;
}

export const RefundCaseDetail: React.FC<RefundCaseDetailProps> = ({ refundId }) => {
  const [refundCase, setRefundCase] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [supportCase, setSupportCase] = useState<any>(null);

  useEffect(() => {
    loadRefundCase();
  }, [refundId]);

  const loadRefundCase = async () => {
    try {
      setLoading(true);
      const response = await apiService.getRefundCase(refundId);
      setRefundCase(response.data);
      
      // Load support case details
      const supportResponse = await apiService.getSupportCase(response.data.support_case_id);
      setSupportCase(supportResponse.data);
    } catch (err: any) {
      setError('Failed to load refund case details');
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
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const calculateDaysDiff = (dateString: string) => {
    const deliveryDate = new Date(dateString);
    const today = new Date();
    const diffTime = Math.abs(today.getTime() - deliveryDate.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  if (loading) {
    return (
      <Card className="refund-case-detail">
        <div className="loading">Loading refund case details...</div>
      </Card>
    );
  }

  if (!refundCase) {
    return (
      <Card className="refund-case-detail">
        <div className="error-message">
          Refund case not found
        </div>
      </Card>
    );
  }

  return (
    <Card className="refund-case-detail">
      <div className="refund-header">
        <h2>Refund Case Details</h2>
        <div className="status-badges">
          <span className={`status-badge ${getStatusBadgeClass(refundCase.status)}`}>
            {refundCase.status}
          </span>
          <span className={`eligibility-badge ${getEligibilityBadgeClass(refundCase.eligibility_status)}`}>
            {refundCase.eligibility_status}
          </span>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="refund-details-grid">
        <div className="detail-section">
          <h3>Basic Information</h3>
          <div className="detail-item">
            <strong>Refund ID:</strong> {refundCase.id}
          </div>
          <div className="detail-item">
            <strong>Support Case ID:</strong> {refundCase.support_case_id}
          </div>
          <div className="detail-item">
            <strong>Customer ID:</strong> {refundCase.customer_id}
          </div>
          <div className="detail-item">
            <strong>Order ID:</strong> {refundCase.order_id}
          </div>
          <div className="detail-item">
            <strong>Created:</strong> {formatDate(refundCase.created_at)}
          </div>
          {refundCase.processed_at && (
            <div className="detail-item">
              <strong>Processed:</strong> {formatDate(refundCase.processed_at)}
            </div>
          )}
        </div>

        <div className="detail-section">
          <h3>Financial Information</h3>
          <div className="detail-item">
            <strong>Total Refund Amount:</strong> ${refundCase.total_refund_amount.toFixed(2)}
          </div>
          {refundCase.rejection_reason && (
            <div className="detail-item">
              <strong>Rejection Reason:</strong> {refundCase.rejection_reason}
            </div>
          )}
        </div>

        <div className="detail-section">
          <h3>Products for Refund</h3>
          <div className="products-list">
            {refundCase.products.map((product: any) => (
              <div key={product.id} className="product-item">
                <div className="product-name">{product.name}</div>
                <div className="product-details">
                  <span>Price: ${product.price?.toFixed(2) || '0.00'}</span>
                  <span>Quantity: {product.quantity || 1}</span>
                  {product.delivery_date && (
                    <span className="delivery-info">
                      Delivered: {formatDate(product.delivery_date)} 
                      ({calculateDaysDiff(product.delivery_date)} days ago)
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {supportCase && (
          <div className="detail-section">
            <h3>Related Support Case</h3>
            <div className="detail-item">
              <strong>Issue Description:</strong> {supportCase.issue_description}
            </div>
            <div className="detail-item">
              <strong>Status:</strong> {supportCase.status}
            </div>
            <div className="detail-item">
              <strong>Created:</strong> {formatDate(supportCase.created_at)}
            </div>
          </div>
        )}

        <div className="detail-section">
          <h3>Refund Reason</h3>
          <div className="refund-reason">
            {refundCase.reason || 'No reason provided'}
          </div>
        </div>
      </div>

      <div className="actions">
        <Button onClick={loadRefundCase}>Refresh</Button>
      </div>
    </Card>
  );
};