import React, { useState, useEffect } from 'react';
import { RefundRequestForm as RefundCaseForm, RefundCaseList, RefundCaseDetail } from '../components';
import { Card } from '../components';
import { validateUUID } from '../services/validation';
import { apiService } from '../services/api';

export const RefundDashboard: React.FC = () => {
  const [customerId, setCustomerId] = useState('');
  const [supportCaseId, setSupportCaseId] = useState('');
  const [activeTab, setActiveTab] = useState<'create' | 'view' | 'details'>('create');
  const [selectedRefundId, setSelectedRefundId] = useState('');
  const [supportCases, setSupportCases] = useState<any[]>([]);
  const [loadingSupportCases, setLoadingSupportCases] = useState(false);

  const handleRefundCreated = (refundId: string) => {
    alert(`Refund request created successfully! Refund ID: ${refundId}`);
    setActiveTab('view');
    setSelectedRefundId(refundId);
  };

  // Fetch customer support cases when customerId changes
  useEffect(() => {
    const fetchSupportCases = async () => {
      if (customerId) {
        setLoadingSupportCases(true);
        try {
          const response = await apiService.getCustomerSupportCases(customerId);
          setSupportCases(response.data);
        } catch (error) {
          console.error('Failed to fetch support cases:', error);
          setSupportCases([]);
        } finally {
          setLoadingSupportCases(false);
        }
      } else {
        setSupportCases([]);
      }
    };

    fetchSupportCases();
  }, [customerId]);

  const customerSupportCases = supportCases.filter(caseItem => 
    caseItem.customer_id === customerId && caseItem.status !== 'Closed'
  );

  const handleRefundSelect = (refundId: string) => {
    setSelectedRefundId(refundId);
    setActiveTab('details');
  };

  return (
    <div className="refund-dashboard">
      <Card>
        <h1>Refund Management Dashboard</h1>
        
        <div className="tab-navigation">
          <button
            className={activeTab === 'create' ? 'active' : ''}
            onClick={() => setActiveTab('create')}
          >
            Request Refund
          </button>
          <button
            className={activeTab === 'view' ? 'active' : ''}
            onClick={() => setActiveTab('view')}
          >
            View Refund Cases
          </button>
          {selectedRefundId && (
            <button
              className={activeTab === 'details' ? 'active' : ''}
              onClick={() => setActiveTab('details')}
            >
              Refund Details
            </button>
          )}
        </div>

        {activeTab === 'create' && (
          <div className="tab-content">
            <h2>Request Refund from Support Case</h2>
            <div className="customer-info-form">
              <label>
                Customer ID:
                <input
                  type="text"
                  value={customerId}
                  onChange={(e) => {
                    setCustomerId(e.target.value);
                    setSupportCaseId('');
                  }}
                  placeholder="e.g., e2281646-b06e-4fcc-930f-cedc34e3e304"
                />
              </label>
              
            {customerId && (
              <div className="support-case-selection">
                <label>
                  Select Support Case:
                  <select
                    value={supportCaseId}
                    onChange={(e) => setSupportCaseId(e.target.value)}
                    disabled={loadingSupportCases}
                  >
                    <option value="">{
                      loadingSupportCases ? 'Loading cases...' : '-- Select a support case --'
                    }</option>
                    {customerSupportCases.map(caseItem => (
                      <option key={caseItem.id} value={caseItem.id}>
                        Support Case #{caseItem.id.slice(-8)} - Order {caseItem.order_id} - {caseItem.status}
                        {caseItem.intends_refund === 'Yes' && ' - 💰 Refund Expected'}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            )}
            </div>

            {customerId && !validateUUID(customerId) && (
              <p className="error-message">
                Please enter a valid Customer ID
              </p>
            )}

            {customerId && supportCaseId && validateUUID(customerId) ? (
              <RefundCaseForm
                supportCaseId={supportCaseId}
                onRefundCreated={handleRefundCreated}
              />
            ) : (
              <p className="info-message">
                {loadingSupportCases 
                  ? 'Loading support cases...'
                  : customerId && customerSupportCases.length === 0 
                    ? 'No support cases found for this customer'
                    : 'Please enter your Customer ID and select a support case to request a refund.'
                }
              </p>
            )}
          </div>
        )}

        {activeTab === 'view' && (
          <div className="tab-content">
            <h2>My Refund Cases</h2>
            <div className="customer-input">
              <label>
                Customer ID:
                <input
                  type="text"
                  value={customerId}
                  onChange={(e) => setCustomerId(e.target.value)}
                  placeholder="e.g., e2281646-b06e-4fcc-930f-cedc34e3e304"
                />
              </label>
              {customerId && !validateUUID(customerId) && (
                <p className="error-message">
                  Please enter a valid Customer ID
                </p>
              )}
              <p className="info-message">
                Enter your Customer ID to view your refund cases.
              </p>
            </div>

            {customerId && validateUUID(customerId) && (
              <RefundCaseList 
                customerId={customerId}
                onRefundSelect={handleRefundSelect}
              />
            )}
          </div>
        )}

        {activeTab === 'details' && selectedRefundId && (
          <div className="tab-content">
            <h2>Refund Case Details</h2>
            <RefundCaseDetail refundId={selectedRefundId} />
          </div>
        )}
      </Card>
    </div>
  );
};