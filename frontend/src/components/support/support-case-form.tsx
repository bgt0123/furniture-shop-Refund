import React from 'react';

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
  onSubmit: (caseData: SupportCase) => void;
  onRefundRequestCreate?: (caseId: string) => void;
  editingCase?: SupportCase | null;
}

const SupportCaseForm: React.FC<SupportCaseFormProps> = ({
  isOpen,
  onClose,
  onSubmit,
  onRefundRequestCreate,
  editingCase
}) => {
  const [formData, setFormData] = React.useState({
    title: '',
    description: '',
    caseType: 'Question' as 'Question' | 'Refund',
    attachments: [] as string[],
    customerName: '',
    contactEmail: '',
    orderNumber: '',
    productSku: '',
    refundReason: '',
    showRefundDetails: false
  });

  React.useEffect(() => {
    if (editingCase) {
      setFormData({
        title: editingCase.title,
        description: editingCase.description,
        caseType: editingCase.caseType,
        attachments: [],
        customerName: '',
        contactEmail: '',
        orderNumber: '',
        productSku: '',
        refundReason: '',
        showRefundDetails: editingCase.caseType === 'Refund'
      });
    } else {
      setFormData({
        title: '',
        description: '',
        caseType: 'Question',
        attachments: [],
        customerName: '',
        contactEmail: '',
        orderNumber: '',
        productSku: '',
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
      caseType: 'Question',
      attachments: [],
      customerName: '',
      contactEmail: '',
      orderNumber: '',
      productSku: '',
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
    if (isOpen) {
      dialogRef.current?.showModal();
    } else {
      dialogRef.current?.close();
    }
  }, [isOpen]);

  React.useEffect(() => {
    // Automatically show refund details when Refund type is selected
    if (formData.caseType === 'Refund' && !formData.showRefundDetails) {
      setFormData(prev => ({ ...prev, showRefundDetails: true }));
    }
  }, [formData.caseType]);

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

        <div className="modal-body">
          <form onSubmit={handleSubmit} className="space-y-6">
            {formData.caseType === 'Refund' && (
              <div className="refund-prerequisites">
                <div className="bg-gradient-to-r from-green-50 to-emerald-100 border-l-4 border-green-500 p-4 rounded-lg mb-6">
                  <h3 className="font-semibold text-green-800 mb-2">📋 Refund Request Prerequisites</h3>
                  <ul className="text-green-700 text-sm space-y-2">
                    <li>• Product must be within 14 days of delivery</li>
                    <li>• Photos of damage/defects required</li>
                    <li>• Original packaging must be retained</li>
                    <li>• Order number and proof of purchase needed</li>
                  </ul>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {formData.caseType === 'Refund' && (
                <div className="md:col-span-2">
                  <div className={`collapsible-section bg-gradient-to-r from-yellow-50 to-yellow-100 border-l-4 border-yellow-500 rounded-lg mb-4 overflow-hidden ${formData.showRefundDetails ? 'active' : ''}`}>
                    <button
                      type="button"
                      onClick={() => setFormData({ ...formData, showRefundDetails: !formData.showRefundDetails })}
                      className="w-full text-left p-4 flex justify-between items-center"
                    >
                      <h3 className="font-semibold text-yellow-800 flex items-center">
                        <span>📋</span>
                        <span className="ml-2">Additional Refund Information Required</span>
                      </h3>
                      <span className="text-yellow-700">{formData.showRefundDetails ? '▲' : '▼'}</span>
                    </button>
                    <div className="collapsible-section-content">
                      <div className="px-4 pb-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="form-label">Order Number *</label>
                            <input
                              type="text"
                              required={formData.caseType === 'Refund'}
                              value={formData.orderNumber}
                              onChange={(e) => setFormData({ ...formData, orderNumber: e.target.value })}
                              className="form-input"
                              placeholder="Order number/receipt ID"
                            />
                          </div>
                          <div>
                            <label className="form-label">Product SKU/ID *</label>
                            <input
                              type="text"
                              required={formData.caseType === 'Refund'}
                              value={formData.productSku}
                              onChange={(e) => setFormData({ ...formData, productSku: e.target.value })}
                              className="form-input"
                              placeholder="Product identifier"
                            />
                          </div>
                        </div>
                        <div className="mt-4">
                          <label className="form-label">Reason for Refund *</label>
                          <textarea
                            required={formData.caseType === 'Refund'}
                            rows={3}
                            value={formData.refundReason}
                            onChange={(e) => setFormData({ ...formData, refundReason: e.target.value })}
                            className="form-input form-textarea"
                            placeholder="Please provide detailed reason for requesting a refund..."
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div className="md:col-span-2">
                <label className="form-label">Case Title</label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="form-input"
                  placeholder="Brief description of the issue"
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
                  placeholder={`Please provide detailed information about the issue...${formData.caseType === 'Refund' ? '\n\nFor refunds: Include details about why a refund is needed.' : ''}`}
                />
              </div>

              <div>
                <label className="form-label">Customer Name (optional)</label>
                <input
                  type="text"
                  value={formData.customerName}
                  onChange={(e) => setFormData({ ...formData, customerName: e.target.value })}
                  className="form-input"
                  placeholder="Full name"
                />
              </div>

              <div>
                <label className="form-label">Contact Email (optional)</label>
                <input
                  type="email"
                  value={formData.contactEmail}
                  onChange={(e) => setFormData({ ...formData, contactEmail: e.target.value })}
                  className="form-input"
                  placeholder="email@example.com"
                />
              </div>

               {formData.caseType === 'Question' && (
                 <div className="md:col-span-2">
                   <label className="form-label">Order Number (optional)</label>
                   <input
                     type="text"
                     value={formData.orderNumber}
                     onChange={(e) => setFormData({ ...formData, orderNumber: e.target.value })}
                     className="form-input"
                     placeholder="Order number/receipt ID"
                   />
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

              <div className="md:col-span-2">
                <label className="form-label">Case Type</label>
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
                {!editingCase && formData.caseType === 'Refund' && (
                  <span className="text-sm text-blue-600 font-medium mr-4">
                    A refund request will be created automatically
                  </span>
                )}
                {editingCase && editingCase.caseType === 'Question' && !editingCase.refund_request_id && editingCase.status !== 'Closed' && formData.caseType === 'Question' && (
                  <button
                    type="button"
                    onClick={() => {
                      if (editingCase && editingCase.id && onRefundRequestCreate) {
                        handleCancel();
                        onRefundRequestCreate(editingCase.id);
                      }
                    }}
                    className="btn btn-refund-request"
                  >
                    Convert to Refund Request
                  </button>
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
                >
                  {editingCase ? 'Update Case' : 'Create Case'}
                </button>
              </div>
          </form>
        </div>
      </div>
    </dialog>
  );
};

export default SupportCaseForm;