import React from 'react';
import { Card } from '../components';
import { RefundCaseAdminList } from '../types/models';

interface AgentRefundListProps {
  cases: RefundCaseAdminList[];
  onCaseSelect: (caseItem: RefundCaseAdminList) => void;
  selectedCaseId?: string;
}

const AgentRefundList: React.FC<AgentRefundListProps> = ({ cases, onCaseSelect, selectedCaseId }) => {
  if (cases.length === 0) {
    return (
      <Card>
        <div className="no-cases">
          <h3>No refund cases found</h3>
          <p>There are no refund cases matching your current filter.</p>
        </div>
      </Card>
    );
  }

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

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div className="agent-refund-list">
      {cases.map((caseItem) => (
        <Card 
          key={caseItem.id} 
          className={`case-item ${caseItem.id === selectedCaseId ? 'selected' : ''}`}
          onClick={() => onCaseSelect(caseItem)}
        >
          <div className="case-header">
            <div className="case-id">Refund #{caseItem.id.slice(0, 8)}...</div>
            <div className="status-badges">
              <span className={`badge badge-${getStatusBadgeVariant(caseItem.status)}`}>
                {caseItem.status}
              </span>
              <span className={`badge badge-${getEligibilityBadgeVariant(caseItem.eligibility_status)}`}>
                {caseItem.eligibility_status}
              </span>
            </div>
          </div>
          
          <div className="case-details">
            <div className="customer-info">
              <strong>Customer:</strong> {caseItem.customer_name}
              <br />
              <em>{caseItem.customer_email}</em>
            </div>
            
            <div className="amount-info">
              <strong>Amount:</strong> {formatCurrency(caseItem.total_refund_amount)}
            </div>
            
            <div className="date-info">
              <strong>Created:</strong> {new Date(caseItem.created_at).toLocaleDateString()}
            </div>
            
            <div className="case-actions">
              <button className="btn btn-primary btn-sm">
                View Details
              </button>
            </div>
          </div>
        </Card>
      ))}

      <style>{`
        .agent-refund-list .case-item {
          cursor: pointer;
          transition: all 0.3s;
          margin-bottom: 10px;
          border-left: 4px solid transparent;
        }
        
        .agent-refund-list .case-item:hover {
          background-color: #f8f9fa;
          border-left-color: #007bff;
        }
        
        .agent-refund-list .case-item.selected {
          background-color: #e7f3ff;
          border-left-color: #007bff;
        }
        
        .case-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;
        }
        
        .case-id {
          font-weight: bold;
          color: #495057;
        }
        
        .status-badges {
          display: flex;
          gap: 8px;
        }
        
        .badge {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: bold;
        }
        
        .badge-warning { background: #fff3cd; color: #856404; }
        .badge-success { background: #d1edde; color: #155724; }
        .badge-danger { background: #f8d7da; color: #721c24; }
        .badge-info { background: #d1ecf1; color: #0c5460; }
        .badge-secondary { background: #e2e3e5; color: #383d41; }
        
        .case-details {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 10px;
        }
        
        .customer-info, .amount-info, .date-info {
          margin-bottom: 8px;
        }
        
        .case-actions {
          grid-column: span 2;
          text-align: right;
        }
        
        .no-cases {
          text-align: center;
          padding: 40px;
          color: #6c757d;
        }
        
        @media (max-width: 768px) {
          .case-details {
            grid-template-columns: 1fr;
          }
          
          .case-actions {
            grid-column: 1;
          }
        }
      `}</style>
    </div>
  );
};

export default AgentRefundList;