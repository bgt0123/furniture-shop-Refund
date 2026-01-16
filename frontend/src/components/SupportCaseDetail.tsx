import React, { useState, useEffect } from 'react';
import { Button, Card } from '../components';
import { apiService } from '../services/api';

interface SupportCaseDetailProps {
  caseId: string;
  onClose: () => void;
  onCaseUpdated?: () => void;
}

interface SupportCase {
  id: string;
  customer_id: string;
  order_id: string;
  products: any[];
  issue_description: string;
  status: string;
  created_at: string;
  closed_at: string | null;
  attachments: any[];
}

export const SupportCaseDetail: React.FC<SupportCaseDetailProps> = ({
  caseId,
  onClose,
  onCaseUpdated
}) => {
  const [caseData, setCaseData] = useState<SupportCase | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  // Note: newAttachment state would be used when implementing attachment functionality

  const loadCase = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getSupportCase(caseId);
      setCaseData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load case details');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCase();
  }, [caseId]);

  const handleCloseCase = async () => {
    try {
      await apiService.closeSupportCase(caseId);
      await loadCase();
      if (onCaseUpdated) {
        onCaseUpdated();
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to close case');
    }
  };

  // Note: Add attachment functionality would be implemented here when needed
  // const handleAddAttachment = async () => { ... };

  if (isLoading) {
    return (
      <Card className="support-case-detail modal-overlay">
        <p>Loading case details...</p>
      </Card>
    );
  }

  if (error || !caseData) {
    return (
      <Card className="support-case-detail modal-overlay">
        <p className="error">{error || 'Case not found'}</p>
        <Button onClick={onClose}>Close</Button>
      </Card>
    );
  }

  return (
    <div className="modal-overlay">
      <Card className="support-case-detail">
        <div className="header">
          <h2>Support Case #{caseData.id.slice(-6)}</h2>
          <Button onClick={onClose}>Close</Button>
        </div>

        <div className="case-info">
          <div className="info-section">
            <h3>Basic Information</h3>
            <p><strong>Case ID:</strong> {caseData.id}</p>
            <p><strong>Customer ID:</strong> {caseData.customer_id}</p>
            <p><strong>Order ID:</strong> {caseData.order_id}</p>
            <p><strong>Status:</strong> {caseData.status}</p>
            <p><strong>Created:</strong> {new Date(caseData.created_at).toLocaleString()}</p>
            {caseData.closed_at && (
              <p><strong>Closed:</strong> {new Date(caseData.closed_at).toLocaleString()}</p>
            )}
          </div>

          <div className="info-section">
            <h3>Products</h3>
            <ul>
              {caseData.products.map((product, index) => (
                <li key={index}>
                  {product.name}
                  {product.price && ` - $${product.price}`}
                </li>
              ))}
            </ul>
          </div>

          <div className="info-section">
            <h3>Issue Description</h3>
            <div className="issue-description">
              {caseData.issue_description}
            </div>
          </div>

          <div className="info-section">
            <h3>Attachments</h3>
            {caseData.attachments.length === 0 ? (
              <p>No attachments</p>
            ) : (
              <ul>
                {caseData.attachments.map((attachment, index) => (
                  <li key={index}>
                    {attachment.filename || `Attachment ${index + 1}`}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="actions">
            {caseData.status === 'Open' && (
              <Button onClick={handleCloseCase}>
                Close Case
              </Button>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};