import React, { useState } from 'react';
import { SupportCaseForm, SupportCaseList } from '../components';
import { Card } from '../components';
import { validateUUID } from '../services/validation';

export const SupportDashboard: React.FC = () => {
  const [customerId, setCustomerId] = useState('');
  const [orderId, setOrderId] = useState('');
  const [activeTab, setActiveTab] = useState<'create' | 'view'>('create');
  const [validationError, setValidationError] = useState('');

  const mockOrders = [
    { id: 'ORD001', customer_id: 'e2281646-b06e-4fcc-930f-cedc34e3e304', products: [
      { id: 'prod-1', name: 'Office Chair', price: 199.99 },
      { id: 'prod-2', name: 'Desk', price: 299.99 }
    ]},
    { id: 'ORD002', customer_id: 'e2281646-b06e-4fcc-930f-cedc34e3e304', products: [
      { id: 'prod-3', name: 'Bookshelf', price: 149.99 },
      { id: 'prod-4', name: 'Lamp', price: 49.99 }
    ]},
    { id: 'ORD003', customer_id: 'f3392757-c17f-5edd-a41g-dedf45f4g415', products: [
      { id: 'prod-5', name: 'Dining Table', price: 599.99 },
      { id: 'prod-6', name: 'Dining Chairs', price: 399.99 }
    ]}
  ];

  const [selectedOrderProducts, setSelectedOrderProducts] = useState<Product[]>([]);

  const handleCaseCreated = (caseId: string) => {
    alert(`Support case created successfully! Case ID: ${caseId}`);
    setActiveTab('view');
  };

  // Filter orders by customer ID and find products for selected order
  const customerOrders = customerId ? mockOrders.filter(order => order.customer_id === customerId) : [];
  const selectedOrder = customerOrders.find(order => order.id === orderId);

  const handleOrderSelect = (orderId: string) => {
    setOrderId(orderId);
    const order = customerOrders.find(o => o.id === orderId);
    setSelectedOrderProducts(order ? order.products : []);
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
                  onChange={(e) => {
                    setCustomerId(e.target.value);
                    setOrderId('');
                    setValidationError('');
                  }}
                  placeholder="e.g., e2281646-b06e-4fcc-930f-cedc34e3e304"
                />
              </label>
              
              {customerId && customerOrders.length > 0 && (
                <div className="order-selection">
                  <label>
                    Select Order:
                    <select
                      value={orderId}
                      onChange={(e) => handleOrderSelect(e.target.value)}
                    >
                      <option value="">-- Select an order --</option>
                      {customerOrders.map(order => (
                        <option key={order.id} value={order.id}>
                          Order #{order.id}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
              )}
            </div>

            {validationError && (
              <p className="error-message">{validationError}</p>
            )}

            {customerId && orderId && selectedOrderProducts.length > 0 ? (
              validateUUID(customerId) ? (
                <SupportCaseForm
                  customerId={customerId}
                  orderId={orderId}
                  products={selectedOrderProducts}
                  onCaseCreated={handleCaseCreated}
                />
              ) : (
                <p className="error-message">
                  Please enter a valid Customer ID
                </p>
              )
            ) : (
              <p className="info-message">
                {customerId && customerOrders.length === 0 
                  ? 'No orders found for this customer'
                  : 'Please enter your Customer ID and select an order to create a support case.'
                }
              </p>
            )}
          </div>
        )}

        {activeTab === 'view' && (
          <div className="tab-content">
            <h2>My Support Cases</h2>
            <div className="customer-input">
              <label>
                Customer ID:
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
              {customerId && !validateUUID(customerId) && (
                <p className="error-message">
                  Please enter a valid Customer ID
                </p>
              )}
              <p className="info-message">
                Enter your Customer ID to view your support cases.
              </p>
            </div>

            {customerId && validateUUID(customerId) && (
              <SupportCaseList customerId={customerId} />
            )}
          </div>
        )}
      </Card>
    </div>
  );
};