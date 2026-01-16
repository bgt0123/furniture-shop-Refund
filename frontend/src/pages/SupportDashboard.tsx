import React, { useState } from 'react';
import { SupportCaseForm, SupportCaseList } from '../components';
import { Card } from '../components';

export const SupportDashboard: React.FC = () => {
  const [customerId, setCustomerId] = useState('');
  const [orderId, setOrderId] = useState('');
  const [activeTab, setActiveTab] = useState<'create' | 'view'>('create');

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
                Customer ID:
                <input
                  type="text"
                  value={customerId}
                  onChange={(e) => setCustomerId(e.target.value)}
                  placeholder="Enter customer ID"
                />
              </label>
              <label>
                Order ID:
                <input
                  type="text"
                  value={orderId}
                  onChange={(e) => setOrderId(e.target.value)}
                  placeholder="Enter order ID"
                />
              </label>
            </div>

            {customerId && orderId ? (
              <SupportCaseForm
                customerId={customerId}
                orderId={orderId}
                products={mockProducts}
                onCaseCreated={handleCaseCreated}
              />
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
              <SupportCaseList customerId={customerId} />
            ) : (
              <div className="customer-input">
                <label>
                  Customer ID:
                  <input
                    type="text"
                    value={customerId}
                    onChange={(e) => setCustomerId(e.target.value)}
                    placeholder="Enter your customer ID"
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