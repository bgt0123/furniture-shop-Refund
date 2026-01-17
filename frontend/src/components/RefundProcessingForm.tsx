import React, { useState } from 'react';
import { Card, Button, LoadingSpinner } from '../components';
import { agentApiService } from '../services/agentApi';
import { RefundCaseAdminList } from '../types/models';

interface RefundProcessingFormProps {
  refundCase: RefundCaseAdminList;
  onProcessed: () => void;
  onCancel: () => void;
}

const RefundProcessingForm: React.FC<RefundProcessingFormProps> = ({ refundCase, onProcessed, onCancel }) => {
  const [action, setAction] = useState<'approve' | 'reject'>('approve');
  const [reason, setReason] = useState('');
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (action === 'reject' && !reason.trim()) {
      setError('Please provide a reason for rejection');
      return;
    }

    try {
      setProcessing(true);
      setError(null);

      if (action === 'approve') {
        await agentApiService.approveRefundCase(refundCase.id);
      } else {
        await agentApiService.rejectRefundCase(refundCase.id, { reason: reason.trim() });
      }

      onProcessed();
    } catch (err: any) {
      setError(err.response?.data?.message || `Failed to ${action} refund case`);
    } finally {
      setProcessing(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'Pending': return 'warning';
      case 'Approved': return 'success';
      case 'Rejected': return 'danger';
      case 'Completed': return 'info';
      default: return 'secondary';
    }
  };

  const getEligibilityBadgeVariant = (status: string) => {
    switch (status) {
      case 'Eligible': return 'success';
      case 'Partially Eligible': return 'warning';
      case 'Ineligible': return 'danger';
      default: return 'secondary';
    }
  };

  return (
    <Card>
      <div className="refund-processing-form">
        <div className="form-header">
          <h3>Process Refund Case</h3>
          <Button onClick={onCancel} variant="secondary">Back to List</Button>
        </div>

        <div className="case-summary">
          <h4>Case Summary</h4>
          <div className="summary-grid">
            <div><strong>Refund ID:</strong> {refundCase.id.slice(0, 8)}...</div>
            <div><strong>Customer:</strong> {refundCase.customer_name} ({refundCase.customer_email})</div>
            <div><strong>Amount:</strong> {formatCurrency(refundCase.total_refund_amount)}</div>
            <div><strong>Status:</strong> <span className={`badge badge-${getStatusBadgeVariant(refundCase.status)}`}>{refundCase.status}</span></div>
            <div><strong>Eligibility:</strong> <span className={`badge badge-${getEligibilityBadgeVariant(refundCase.eligibility_status)}`}>{refundCase.eligibility_status}</span></div>
            <div><strong>Created:</strong> {new Date(refundCase.created_at).toLocaleDateString()}</div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="processing-form">
          <div className="form-section">
            <h4>Select Action</h4>
            <div className="action-buttons">
              <button
                type="button"
                className={`action-btn ${action === 'approve' ? 'active approve' : ''}`}
                onClick={() => setAction('approve')}
              >
                ✓ Approve Refund
              </button>
              <button
                type="button"
                className={`action-btn ${action === 'reject' ? 'active reject' : ''}`}
                onClick={() => setAction('reject')}
              >
                ✗ Reject Refund
              </button>
            </div>
          </div>

          {action === 'reject' && (
            <div className="form-section">
              <h4>Rejection Reason</h4>
              <textarea
                value={reason}
                onChange={(e) => {
                  setReason(e.target.value);
                  setError(null);
                }}
                placeholder="Please provide a reason for rejecting this refund request..."
                rows={4}
                className={`form-textarea ${error ? 'error' : ''}`}
              />
              {error && action === 'reject' && <div className="error-message">{error}</div>}
            </div>
          )}

          <div className="form-actions">
            <Button 
              type="button" 
              onClick={onCancel} 
              variant="secondary"
              disabled={processing}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              variant="primary"
              disabled={processing || (action === 'reject' && !reason.trim())}
            >
              {processing ? (
                <><LoadingSpinner size="sm" /> Processing...</>
              ) : action === 'approve' ? (
                'Approve Refund'
              ) : (
                'Reject Refund'
              )}
            </Button>
          </div>

          {error && action !== 'reject' && <div className="error-message">{error}</div>}
        </form>

        <style>{`
          .refund-processing-form {
            padding: 20px;
          }
          
          .form-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
          }
          
          .case-summary {
            margin-bottom: 30px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
          }
          
          .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 10px;
            margin-top: 10px;
          }
          
          .form-section {
            margin-bottom: 20px;
          }
          
          .action-buttons {
            display: flex;
            gap: 10px;
            margin-top: 10px;
          }
          
          .action-btn {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #ddd;
            border-radius: 8px;
            background: white;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 16px;
            font-weight: bold;
          }
          
          .action-btn.active {
            border-color: #007bff;
            background-color: #e7f3ff;
          }
          
          .action-btn.approve.active {
            border-color: #28a745;
            background-color: #d4edda;
            color: #155724;
          }
          
          .action-btn.reject.active {
            border-color: #dc3545;
            background-color: #f8d7da;
            color: #721c24;
          }
          
          .action-btn:hover {
            background-color: #f8f9fa;
          }
          
          .form-textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
            resize: vertical;
          }
          
          .form-textarea.error {
            border-color: #dc3545;
          }
          
          .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
          }
          
          .error-message {
            color: #dc3545;
            padding: 10px;
            background-color: #f8d7da;
            border-radius: 4px;
            margin-top: 10px;
          }
          
          .badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
          }
          
          .badge-warning { background: #fff3cd; color: #856404; }
          .badge-success { background: #d1edde; color: #155724; }
          .badge-danger { background: #f8d7da; color: #721c24; }
          .badge-info { background: #d1ecf1; color: #0c5460; }
          
          @media (max-width: 768px) {
            .action-buttons {
              flex-direction: column;
            }
            
            .summary-grid {
              grid-template-columns: 1fr;
            }
            
            .form-actions {
              flex-direction: column;
            }
          }
        `}</style>
      </div>
    </Card>
  );
};

export default RefundProcessingForm;