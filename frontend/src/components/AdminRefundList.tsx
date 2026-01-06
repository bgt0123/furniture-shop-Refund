import React from 'react'
import { Link } from 'react-router-dom'
import { RefundCase } from '../../types/refundTypes'
import { Button } from '../Button'

interface AdminRefundListProps {
  cases: RefundCase[]
  onViewDetails: (refundId: string) => void
  onApprove: (refundId: string) => void
  onReject: (refundId: string) => void
  token: string
}

export const AdminRefundList: React.FC<AdminRefundListProps> = ({ 
  cases, 
  onViewDetails, 
  onApprove, 
  onReject,
  token 
}) => {
  if (cases.length === 0) {
    return (
      <div className="admin-refund-list empty">
        <p>No refund cases found.</p>
        <Link to="/admin">
          <Button variant="primary">Return to Dashboard</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="admin-refund-list">
      <h2>All Refund Cases</h2>

      <div className="admin-case-grid">
        {cases.map((refundCase) => (
          <div key={refundCase.id} className="admin-case-card">
            <div className="admin-case-header">
              <span className={`status-badge ${refundCase.status.toLowerCase()}`}>
                {refundCase.status}
              </span>
              <span className="case-id">Refund #{refundCase.id.substring(0, 8)}</span>
            </div>
            
            <div className="admin-case-body">
              <p className="customer-info">
                Customer: {refundCase.customerId.substring(0, 8)}...
              </p>
              <p className="support-case">
                Support Case: {refundCase.supportCaseId.substring(0, 8)}...
              </p>
              <p className="order-info">Order: {refundCase.orderId}</p>
              <p className="created-at">
                Requested: {new Date(refundCase.createdAt).toLocaleString()}
              </p>
              <p className="eligibility">
                Eligibility: <span className={`eligibility-${refundCase.eligibilityStatus.toLowerCase()}`}>
                  {refundCase.eligibilityStatus}
                </span>
              </p>
              <p className="amount">Amount: ${refundCase.totalRefundAmount.toFixed(2)}</p>
              <p className="products-count">Products: {refundCase.products?.length || 0}</p>
              
              {refundCase.status === 'Rejected' && refundCase.rejectionReason && (
                <p className="rejection-reason">
                  Rejected: {refundCase.rejectionReason}
                </p>
              )}
              
              {refundCase.status === 'Approved' && refundCase.processedAt && (
                <p className="processed-at">
                  Processed: {new Date(refundCase.processedAt).toLocaleString()}
                </p>
              )}
            </div>
            
            <div className="admin-case-actions">
              <Button 
                variant="secondary" 
                onClick={() => onViewDetails(refundCase.id)}
                size="small"
              >
                View Details
              </Button>
              
              {refundCase.status === 'Pending' && (
                <>
                  <Button
                    variant="success"
                    onClick={() => onApprove(refundCase.id)}
                    size="small"
                  >
                    Approve
                  </Button>
                  
                  <Button
                    variant="danger"
                    onClick={() => onReject(refundCase.id)}
                    size="small"
                  >
                    Reject
                  </Button>
                </>
              )}
              
              {refundCase.status === 'Approved' && (
                <Button
                  variant="primary"
                  onClick={() => onViewDetails(refundCase.id)}
                  size="small"
                >
                  Complete Processing
                </Button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}