import React from 'react';

interface Customer {
  id: string;
  name: string;
  email: string;
}

interface Product {
  id: string;
  name: string;
}

interface CustomerOrder {
  orderId: string;
  products: Product[];
  deliveryDate: string;
  status: string;
}

interface MockData {
  customers: Customer[];
  products: Product[];
  customerOrders: Record<string, CustomerOrder[]>;
}

interface SupportCase {
  id?: string;
  caseNumber?: string;
  title: string;
  description: string;
  caseType: 'Question' | 'Refund';
  status?: 'Open' | 'In Progress' | 'Closed';
  refund_request_id?: string;
  created?: string;
  updated?: string;
}

interface SupportCaseFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (caseData: { 
    title: string; 
    description: string; 
    caseType: 'Question' | 'Refund'; 
    customerId: string;
    orderId?: string; 
    deliveryDate?: string; 
    productIds?: string[]; 
    refundReason?: string; 
  }) => void;
  editingCase?: SupportCase | null;
  currentUser?: {
    id: string;
    role: string;
    name: string;
  };
}

const SupportCaseForm: React.FC<SupportCaseFormProps> = ({
  isOpen,
  onClose,
  onSubmit,
  editingCase,
  currentUser
}) => {
 const [formData, setFormData] = React.useState({
      title: '',
      description: '',
      customerId: '',
      caseType: 'Question' as 'Question' | 'Refund',
      attachments: [] as string[],
      orderId: '',
      deliveryDate: '',
      productIds: [] as string[],
      refundReason: '',
      showRefundDetails: false
    });

 const [mockData, setMockData] = React.useState<MockData | null>(null);
 const [selectedCustomer, setSelectedCustomer] = React.useState<Customer | null>(null);
 const [customerOrders, setCustomerOrders] = React.useState<CustomerOrder[]>([]);
 const [availableProducts, setAvailableProducts] = React.useState<Product[]>([]);

  React.useEffect(() => {
    if (editingCase) {
       setFormData({
         title: editingCase.title,
         description: editingCase.description,
         customerId: '',
         caseType: editingCase.caseType,
         attachments: [],
         orderId: '',
         deliveryDate: '',
         productIds: [],
         refundReason: '',
         showRefundDetails: editingCase.caseType === 'Refund'
       });
    } else {
       setFormData({
         title: '',
         description: '',
         customerId: '',
         caseType: 'Question',
         attachments: [],
         orderId: '',
         deliveryDate: '',
         productIds: [],
         refundReason: '',
         showRefundDetails: false
       });
    }
  }, [editingCase, isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
    onClose();
  };

   const handleCancel = () => {
    setFormData({
        title: '',
        description: '',
        customerId: '',
        caseType: 'Question',
        attachments: [],
        orderId: '',
        deliveryDate: '',
        productIds: [],
        refundReason: '',
        showRefundDetails: false
      });
     onClose();
   };

  const handleAddAttachment = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const fileNames = files.map(file => file.name);
    setFormData(prev => ({
      ...prev,
      attachments: [...prev.attachments, ...fileNames]
    }));
  };

  // Use dialog element for proper modal behavior
  const dialogRef = React.useRef<HTMLDialogElement>(null);

  

  React.useEffect(() => {
    // Update customer orders when customer changes
    if (mockData && formData.customerId) {
      const orders = mockData.customerOrders[formData.customerId] || [];
      setCustomerOrders(orders);
      
      // Reset order selection when customer changes
      setFormData(prev => ({ ...prev, orderId: '' }));
      
      // Find and set selected customer
      const customer = mockData.customers.find(c => c.id === formData.customerId);
      setSelectedCustomer(customer || null);
    }
  }, [formData.customerId, mockData]);

  React.useEffect(() => {
    // Update available products when order changes
    if (formData.orderId && customerOrders.length > 0) {
      const order = customerOrders.find(o => o.orderId === formData.orderId);
      setAvailableProducts(order?.products || []);
    } else {
      setAvailableProducts([]);
    }
  }, [formData.orderId, customerOrders]);

  React.useEffect(() => {
    // Automatically show refund details when Refund type is selected
    if (formData.caseType === 'Refund' && !formData.showRefundDetails) {
      setFormData(prev => ({ ...prev, showRefundDetails: true }));
    }
  }, [formData.caseType]);

  // Properly manage modal state
  React.useEffect(() => {
    if (!isOpen) {
      dialogRef.current?.close();
      return;
    }
    
    // Only open if not already open
    if (!dialogRef.current?.open) {
      dialogRef.current?.showModal();
    }
    
    // Load mock data when modal opens
    const loadMockData = async () => {
      try {
        const response = await fetch('/final_mock_data.json');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setMockData(data);
      } catch (error) {
        console.error('Failed to load mock data:', error);
        setMockData({ customers: [], products: [], customerOrders: {} });
      }
    };
    
    loadMockData();
  }, [isOpen]);

  if (isOpen && !mockData) {
    return (
      <dialog
        ref={dialogRef}
        className="dialog-modal"
        onClose={handleCancel}
      >
        <div className="modal-container">
          <div className="modal-header">
            <h2 className="modal-title">
              {editingCase ? '✏️ Edit Support Case' : '➕ Create New Support Case'}
            </h2>
            <button
              onClick={handleCancel}
              className="modal-close-btn"
            >
              ×
            </button>
          </div>
          <div className="modal-body text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Loading data...</p>
          </div>
        </div>
      </dialog>
    );
  }

  return (
    <dialog
      ref={dialogRef}
      className="dialog-modal"
      onClose={handleCancel}
    >
      <div className="modal-container">
        <div className="modal-header">
          <h2 className="modal-title">
            {editingCase ? '✏️ Edit Support Case' : '➕ Create New Support Case'}
          </h2>
          {editingCase && currentUser && (
            <span className="user-role-badge">
              Logged in as: {currentUser.name} ({currentUser.role})
            </span>
          )}
          <button
            onClick={handleCancel}
            className="modal-close-btn"
          >
            ×
          </button>
        </div>

        <div className="modal-body">
           <form onSubmit={handleSubmit} className="space-y-6">
             <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="md:col-span-2">
                  <label className="form-label">Case Title</label>
                  <input
                    type="text"
                    required
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="form-input"
                    placeholder="Brief description of the issue"
                    disabled={!!(editingCase && currentUser?.role === 'agent')}
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="form-label">Detailed Description</label>
                  <textarea
                    required
                    rows={5}
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="form-input form-textarea"
                    placeholder="Please provide detailed information about the issue..."
                    disabled={!!(editingCase && currentUser?.role === 'agent')}
                  />
                </div>

                 <div className="md:col-span-2">
                   <label className="form-label">Select Customer *</label>
                   <select
                     required
                     value={formData.customerId}
                     onChange={(e) => setFormData({ ...formData, customerId: e.target.value })}
                     className="form-input"
                   >
                     <option value="">Choose a customer...</option>
                     {mockData ? (
                       mockData.customers && mockData.customers.length > 0 ? (
                         mockData.customers.map(customer => (
                           <option key={customer.id} value={customer.id}>
                             {customer.name} ({customer.email})
                           </option>
                         ))
                       ) : (
                         <option value="" disabled>No customers found in mock data</option>
                       )
                     ) : (
                       <option value="" disabled>Loading customers...</option>
                     )}
                   </select>
                 </div>

                 {formData.customerId && selectedCustomer && (
                   <div className="md:col-span-2 p-3 bg-blue-50 rounded-lg">
                     <p className="text-sm text-blue-800">
                       <strong>Selected Customer:</strong> {selectedCustomer.name} ({selectedCustomer.email})
                     </p>
                   </div>
                 )}

               <div className="md:col-span-2">
                 <label className="form-label">Case Type *</label>
                 <div className="type-selector-grid">
                   <label className={`type-option ${formData.caseType === 'Question' ? 'selected' : ''}`}>
                     <input
                       type="radio"
                       name="caseType"
                       value="Question"
                       checked={formData.caseType === 'Question'}
                       onChange={(e) => setFormData({ ...formData, caseType: e.target.value as 'Question' | 'Refund' })}
                       className="sr-only"
                     />
                     <div className="type-content">
                       <span className="type-icon">❓</span>
                       <div className="type-info">
                         <h4>General Question</h4>
                         <p>For product inquiries, assembly help, or general support questions</p>
                       </div>
                     </div>
                   </label>
                   <label className={`type-option ${formData.caseType === 'Refund' ? 'selected refund' : ''}`}>
                     <input
                       type="radio"
                       name="caseType"
                       value="Refund"
                       checked={formData.caseType === 'Refund'}
                       onChange={(e) => setFormData({ ...formData, caseType: e.target.value as 'Question' | 'Refund' })}
                       className="sr-only"
                     />
                     <div className="type-content">
                       <span className="type-icon">💰</span>
                       <div className="type-info">
                         <h4>Refund Request</h4>
                         <p>For damaged, defective, or incorrect products requiring refund</p>
                       </div>
                     </div>
                   </label>
                 </div>
               </div>

               {formData.caseType === 'Refund' && (
                 <div className="md:col-span-2">
                   <div className="bg-gradient-to-r from-green-50 to-emerald-100 border-l-4 border-green-500 p-4 rounded-lg mb-4">
                     <h3 className="font-semibold text-green-800 mb-2">📋 Refund Request Information</h3>
                     <p className="text-green-700 text-sm mb-4">
                       Please provide the following required information for your refund request:
                     </p>
                   </div>
                   
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="form-label">Select Order *</label>
                        <select
                          required
                          value={formData.orderId}
                          onChange={(e) => setFormData({ ...formData, orderId: e.target.value })}
                          className="form-input"
                        >
                          <option value="">Choose an order...</option>
                          {customerOrders.length > 0 ? customerOrders.map(order => (
                            <option key={order.orderId} value={order.orderId}>
                              {order.orderId} ({order.status}) - {order.products.length} products
                            </option>
                          )) : (
                            <option value="" disabled>{formData.customerId ? 'No orders found for this customer' : 'Select a customer first'}</option>
                          )}
                        </select>
                      </div>
                      <div>
                        <label className="form-label">Delivery Date *</label>
                        <input
                          type="date"
                          required
                          value={formData.orderId ? customerOrders.find(o => o.orderId === formData.orderId)?.deliveryDate || '' : formData.deliveryDate}
                          onChange={(e) => setFormData({ ...formData, deliveryDate: e.target.value })}
                          className="form-input"
                          placeholder="Date delivered"
                          readOnly={!!formData.orderId}
                        />
                      </div>
                    </div>
                    
                    {formData.orderId && (
                      <div>
                        <label className="form-label">Select Products *</label>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-48 overflow-y-auto">
                          {availableProducts.length > 0 ? availableProducts.map(product => (
                            <label key={product.id} className="flex items-center space-x-2 p-2 border rounded cursor-pointer hover:bg-gray-50">
                              <input
                                type="checkbox"
                                checked={formData.productIds.includes(product.id)}
                                onChange={(e) => {
                                  const newProductIds = e.target.checked
                                    ? [...formData.productIds, product.id]
                                    : formData.productIds.filter(id => id !== product.id);
                                  setFormData({ ...formData, productIds: newProductIds });
                                }}
                                className="form-checkbox"
                              />
                              <span className="text-sm">{product.name}</span>
                            </label>
                          )) : (
                            <p className="text-gray-500 text-sm">{formData.orderId ? 'No products available for this order' : 'Select an order first'}</p>
                          )}
                        </div>
                        {formData.productIds.length > 0 && (
                          <p className="text-sm text-green-600 mt-2">
                            Selected {formData.productIds.length} product(s)
                          </p>
                        )}
                      </div>
                    )}
                   
                   <div className="mb-4">
                     <label className="form-label">Reason for Refund *</label>
                     <textarea
                       required
                       rows={3}
                       value={formData.refundReason}
                       onChange={(e) => setFormData({ ...formData, refundReason: e.target.value })}
                       className="form-input form-textarea"
                       placeholder="Please provide detailed reason for requesting a refund..."
                     />
                   </div>
                 </div>
               )}

                 {formData.caseType === 'Question' && (
                   <div className="md:col-span-2">
                     <label className="form-label">Select Order (optional)</label>
                     <select
                       value={formData.orderId}
                       onChange={(e) => setFormData({ ...formData, orderId: e.target.value })}
                       className="form-input"
                     >
                       <option value="">Choose an order...</option>
                       {customerOrders.length > 0 ? customerOrders.map(order => (
                         <option key={order.orderId} value={order.orderId}>
                           {order.orderId} ({order.status}) - {order.products.length} products
                         </option>
                       )) : (
                         <option value="" disabled>{formData.customerId ? 'No orders found for this customer' : 'Select a customer first'}</option>
                       )}
                     </select>
                   </div>
                 )}

               <div className="md:col-span-2">
                 <label className="form-label">Attachments ({formData.attachments.length} files)</label>
                 <input
                   type="file"
                   multiple
                   onChange={handleAddAttachment}
                   className="form-input"
                   accept="image/*,.pdf,.doc,.docx"
                 />
                 {formData.attachments.length > 0 && (
                   <div className="mt-2 text-sm text-gray-600">
                     Files: {formData.attachments.join(', ')}
                   </div>
                 )}
               </div>
             </div>

               <div className="modal-actions">
                 {formData.caseType === 'Refund' && (
                   <div className="relative w-full mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                     <div className="flex items-center justify-between">
                       <div className="flex items-center">
                         <span className="text-blue-600 text-lg mr-2">ℹ️</span>
                         <span className="text-blue-800 font-medium">Refund Request Created</span>
                       </div>
                       <span className="text-blue-700 text-sm">Case type set to Refund</span>
                     </div>
                     <p className="text-blue-600 text-sm mt-1">
                       This support case is configured as a refund request. When you save this case, 
                       a refund request will be automatically created.
                     </p>
                   </div>
                 )}
                 {editingCase && currentUser?.role === 'agent' && (
                   <span className="text-sm text-gray-500 ml-auto mr-4">
                     Agents can only view cases, not edit them
                   </span>
                 )}
                 {!editingCase && formData.caseType === 'Refund' && (
                   <span className="text-sm text-blue-600 font-medium mr-4">
                     A refund request will be created automatically
                   </span>
                 )}
                 {editingCase && editingCase.caseType === 'Question' && !editingCase.refund_request_id && editingCase.status === 'Closed' && (
                   <span className="text-sm text-gray-500 ml-auto mr-4">
                     Cannot create refund request for closed Question cases
                   </span>
                 )}
                 {editingCase && editingCase.refund_request_id && formData.caseType === 'Question' && (
                   <span className="text-sm text-gray-500 ml-auto mr-4">
                     This case already has an associated refund request
                   </span>
                 )}
                 <button 
                   type="button" 
                   onClick={handleCancel} 
                   className="btn btn-cancel"
                 >
                   Cancel
                 </button>
                 <button 
                   type="submit" 
                   className="btn btn-submit"
                   disabled={!!(editingCase && currentUser?.role === 'agent')}
                 >
                   {editingCase ? (currentUser?.role === 'agent' ? 'View Only (Agent)' : 'Update Case') : 'Create Case'}
                 </button>
               </div>
           </form>
         </div>
       </div>
     </dialog>
  );
};

export default SupportCaseForm;