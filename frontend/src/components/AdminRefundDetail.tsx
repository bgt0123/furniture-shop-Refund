import React, { useState } from 'react'
import { RefundCase } from '../../types/refundTypes'
import { Button } from '../Button'
import { Modal } from '../Modal'

interface AdminRefundDetailProps {
  refundCase: RefundCase
  onClose: () => void
  onApprove: () => void
  onReject: (reason: string) => void
  onComplete: () => void
  token: string
}

export const AdminRefundDetail: React.FC<AdminRefundDetailProps> = ({ 
  refundCase, 
  onClose, 
  onApprove, 
  onReject, 
  onComplete,
  token 
}) => {
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [rejectionReason, setRejectionReason] = useState('')

  const handleApprove = () => {
    if (window.confirm('Are you sure you want to approve this refund?')) {
      onApprove()
    }
  }

  const handleReject = () => {
    setShowRejectModal(true)
  }

  const handleComplete = () => {
    if (window.confirm('Are you sure you want to mark this refund as completed?')) {
      onComplete()
    }
  }

  const submitRejection = () => {
    if (rejectionReason.trim()) {
      onReject(rejectionReason)
      setShowRejectModal(false)
      setRejectionReason('')
    }
  }

  return (
    <div className="admin-refund-detail">
      <div className="detail-header">
        <h2>Refund Case Details</h2>
        <Button variant="secondary" onClick={onClose} size="small">
          Close
        </Button>
      </div>

      <div className="detail-content">
        <div className="detail-section">
          <h3>Basic Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Refund ID:</span>
              <span className="info-value">{refundCase.id}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Status:</span>
              <span className={`info-value status-${refundCase.status.toLowerCase()}`}>
                {refundCase.status}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Customer ID:</span>
              <span className="info-value">{refundCase.customerId}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Support Case ID:</span>
              <span className="info-value">{refundCase.supportCaseId}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Order ID:</span>
              <span className="info-value">{refundCase.orderId}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Created At:</span>
              <span className="info-value">
                {new Date(refundCase.createdAt).toLocaleString()}
              </span>
            </div>
            {refundCase.processedAt && (
              <div className="info-item">
                <span className="info-label">Processed At:</span>
                <span className="info-value">
                  {new Date(refundCase.processedAt).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="detail-section">
          <h3>Financial Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Total Refund Amount:</span>
              <span className="info-value amount">
                ${refundCase.totalRefundAmount.toFixed(2)}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Eligibility Status:</span>
              <span className={`info-value eligibility-${refundCase.eligibilityStatus.toLowerCase()}`}>
                {refundCase.eligibilityStatus}
              </span>
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h3>Products</h3>
          <div className="products-table">
            <table>
              <thead>
                <tr>
                  <th>Product ID</th>
                  <th>Name</th>
                  <th>Quantity</th>
                  <th>Price</th>
                  <th>Refund Amount</th>
                  <th>Eligibility</th>
                </tr>
              </thead>
              <tbody>
                {refundCase.products?.map((product, index) => (
                  <tr key={index}> 
                    <td>{product.productId.substring(0, 8)}...</td>
                    <td>{product.name}</td>
                    <td>{product.quantity}</td>
                    <td>${product.price?.toFixed(2) || '0.00'}</td>
                    <td>${product.refundAmount?.toFixed(2) || '0.00'}</td>
                    <td className={`eligibility-${product.eligibility?.toLowerCase()}`}>
                      {product.eligibility || 'Unknown'}
                    </td>
                  </tr>
                )) || (
                  <tr>
                    <td colSpan={6}>No products found</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {refundCase.status === 'Rejected' && refundCase.rejectionReason && (
          <div className="detail-section">
            <h3>Rejection Information</h3>
            <div className="rejection-info">
              <p><strong>Reason:</strong> {refundCase.rejectionReason}</p>
            </div>
          </div>
        )}

        <div className="detail-actions">
          {refundCase.status === 'Pending' && (
            <>
              <Button variant="success" onClick={handleApprove}>
                Approve Refund
              </Button>
              <Button variant="danger" onClick={handleReject}>
                Reject Refund
              </Button>
            </>
          )}

          {refundCase.status === 'Approved' && (
            <Button variant="primary" onClick={handleComplete}>
              Mark as Completed
            </Button>
          )}

          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>

      {/* Rejection Modal */}
      {showRejectModal && (
        <Modal title="Reject Refund" onClose={() => setShowRejectModal(false)}>
          <div className="rejection-modal">
            <p>Please provide a reason for rejecting this refund request:</p>
            <textarea
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              placeholder="Enter rejection reason..."
              rows={4}
              className="rejection-textarea"
            />
            <div className="modal-actions">
              <Button
                variant="danger"
                onClick={submitRejection}
                disabled={!rejectionReason.trim()}
              >
                Confirm Rejection
              </Button>
              <Button
                variant="secondary"
                onClick={() => setShowRejectModal(false)}
              >
                Cancel
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}