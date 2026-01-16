import React, { useState, useEffect } from 'react';
import { Button, Card } from '../components';
import { apiService } from '../services/api';
import { SupportCaseDetail } from './SupportCaseDetail';

interface SupportCase {
  id: string;
  customer_id: string;
  order_id: string;
  products: any[];
  issue_description: string;
  status: string;
  created_at: string;
  closed_at: string | null;
}

interface SupportCaseListProps {
  customerId: string;
}

export const SupportCaseList: React.FC<SupportCaseListProps> = ({ customerId }) => {
  const [cases, setCases] = useState<SupportCase[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);

  const loadCases = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getCustomerSupportCases(customerId);
      setCases(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load cases');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCases();
  }, [customerId]);

  const handleCloseCase = async (caseId: string) => {
    try {
      await apiService.closeSupportCase(caseId);
      await loadCases(); // Reload cases to get updated status
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to close case');
    }
  };

  if (isLoading) {
    return (
      <Card>
        <p>Loading support cases...</p>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <p className="error">{error}</p>
        <Button onClick={loadCases}>Retry</Button>
      </Card>
    );
  }

  const openCase = cases.filter(c => c.status === 'Open');
  const closedCase = cases.filter(c => c.status === 'Closed');

  return (
    <div className="support-case-list">
      <Card>
        <h2>Support Cases</h2>
        
        <h3>Open Cases ({openCase.length})</h3>
        {openCase.length === 0 ? (
          <p>No open support cases found.</p>
        ) : (
          <div className="cases-grid">
            {openCase.map(supportCase => (
              <Card key={supportCase.id} className="case-card">
                <h4>Case #{supportCase.id.slice(-6)}</h4>
                <p><strong>Order:</strong> {supportCase.order_id}</p>
                <p><strong>Products:</strong> {supportCase.products.length}</p>
                <p><strong>Created:</strong> {new Date(supportCase.created_at).toLocaleDateString()}</p>
                
                <div className="case-actions">
                  <Button
                    variant="secondary"
                    onClick={() => setSelectedCaseId(supportCase.id)}
                  >
                    View Details
                  </Button>
                  <Button onClick={() => handleCloseCase(supportCase.id)}>
                    Close Case
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}

        <h3>Closed Cases ({closedCase.length})</h3>
        {closedCase.length === 0 ? (
          <p>No closed support cases found.</p>
        ) : (
          <div className="cases-grid">
            {closedCase.map(supportCase => (
              <Card key={supportCase.id} className="case-card closed">
                <h4>Case #{supportCase.id.slice(-6)}</h4>
                <p><strong>Order:</strong> {supportCase.order_id}</p>
                <p><strong>Products:</strong> {supportCase.products.length}</p>
                <p><strong>Closed:</strong> {supportCase.closed_at && new Date(supportCase.closed_at).toLocaleDateString()}</p>
                
                <div className="case-actions">
                  <Button
                    variant="secondary"
                    onClick={() => setSelectedCaseId(supportCase.id)}
                  >
                    View Details
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </Card>

      {selectedCaseId && (
        <SupportCaseDetail
          caseId={selectedCaseId}
          onClose={() => setSelectedCaseId(null)}
          onCaseUpdated={loadCases}
        />
      )}
    </div>
  );
};