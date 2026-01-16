import React, { useState } from 'react';
import { SupportCaseForm, SupportCaseList } from '../components';
import { Card } from '../components';
import { validateUUID } from '../services/validation';

export const SupportDashboard: React.FC = () => {
  const [customerId, setCustomerId] = useState('');
  const [orderId, setOrderId] = useState('');
  const [activeTab, setActiveTab] = useState<'create' | 'view'>('create');
  const [validationError, setValidationError] = useState('');

  const mockProducts = [
    { id: 'prod-1', name: 'Office Chair', price: 199.99 },
    { id: 'prod-2', name: 'Desk', price: 299.99 },
    { id: 'prod-3', name: 'Bookshelf', price: 149.99 },
    { id: 'prod-4', name: 'Lamp', price: 49.99 }
  ];

  const handleCaseCreated = (caseId: string) => {
    alert(`Support case created successfully! Case ID: ${caseId}`);
    setActiveTab('view');
  };

  return (
    <div className="support-dashboard">
      <Card>
        <h1>Customer Support Dashboard</h1>
        
        <div className="tab-navigation">
          <button
            className={activeTab === 'create' ? 'active' : ''}
            onClick={() => setActiveTab('create')}
          >
            Create New Case
          </button>
          <button
            className={activeTab === 'view' ? 'active' : ''}
            onClick={() => setActiveTab('view')}
          >
            View My Cases
          </button>
        </div>

        {activeTab === 'create' && (
          <div className="tab-content">
            <h2>Create New Support Case</h2>
            <div className="customer-info-form">
              <label>
                Customer ID (UUID format):
                <input
                  type="text"
                  value={customerId}
                  onChange={(e) => {
                    setCustomerId(e.target.value);
                    setValidationError('');
                  }}
                  placeholder="e.g., e2281646-b06e-4fcc-930f-cedc34e3e304"
                />
              </label>
              <label>
                Order ID (UUID format):
                <input
                  type="text"
                  value={orderId}
                  onChange={(e) => {
                    setOrderId(e.target.value);
                    setValidationError('');
                  }}
                  placeholder="e.g., e2281646-b06e-4fcc-930f-cedc34e3e304"
                />
              </label>
            </div>

            {validationError && (
              <p className="error-message">{validationError}</p>
            )}

            {customerId && orderId ? (
              validateUUID(customerId) && validateUUID(orderId) ? (
                <SupportCaseForm
                  customerId={customerId}
                  orderId={orderId}
                  products={mockProducts}
                  onCaseCreated={handleCaseCreated}
                />
              ) : (
                <p className="error-message">
                  Please enter valid UUID format for both Customer ID and Order ID
                </p>
              )
            ) : (
              <p className="info-message">
                Please enter your Customer ID and Order ID to create a support case.
              </p>
            )}
          </div>
        )}

        {activeTab === 'view' && (
          <div className="tab-content">
            <h2>My Support Cases</h2>
            {customerId ? (
              validateUUID(customerId) ? (
                <SupportCaseList customerId={customerId} />
              ) : (
                <div className="customer-input">
                  <p className="error-message">
                    Please enter a valid Customer ID in UUID format
                  </p>
                  <label>
                    Customer ID (UUID):
                    <input
                      type="text"
                      value={customerId}
                      onChange={(e) => {
                        setCustomerId(e.target.value);
                        setValidationError('');
                      }}
                      placeholder="e.g., e2281646-b06e-4fcc-930f-cedc34e3e304"
                    />
                  </label>
                </div>
              )
            ) : (
              <div className="customer-input">
                <label>
                  Customer ID (UUID format):
                  <input
                    type="text"
                    value={customerId}
                    onChange={(e) => {
                      setCustomerId(e.target.value);
                      setValidationError('');
                    }}
                    placeholder="e.g., e2281646-b06e-4fcc-930f-cedc34e3e304"
                  />
                </label>
                <p className="info-message">
                  Enter your Customer ID to view your support cases.
                </p>
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
};