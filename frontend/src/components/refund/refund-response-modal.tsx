import React, { useRef, useEffect, useState } from 'react';

interface RefundResponseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmitDecision: (decision: RefundDecision) => Promise<void>;
  isSubmitting: boolean;
  refundData: {
    refund_request_id: string;
    refund_amount?: { amount: number; currency: string };
    eligibility?: {
      is_eligible: boolean;
      reasons: string[];
      calculated_refund_amount?: number;
      eligibility_date?: string;
    };
    status: string;
    decision_reason?: string;
    created_at: string;
    updated_at: string;
    product_ids: string[];
  };
}

export interface RefundDecision {
  response_type: 'approval' | 'rejection' | 'request_additional_evidence';
  response_content: string;
  refund_amount?: string;
  refund_method?: 'money' | 'voucher' | 'replacement';
}

const RefundResponseModal: React.FC<RefundResponseModalProps> = ({ 
  isOpen, 
  onClose, 
  onSubmitDecision,
  isSubmitting,
  refundData 
}) => {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [decisionType, setDecisionType] = useState<'approval' | 'rejection' | 'request_additional_evidence'>('approval');
  const [responseContent, setResponseContent] = useState('');
  const [refundAmount, setRefundAmount] = useState(refundData.eligibility?.calculated_refund_amount?.toString() || '');
  const [refundMethod, setRefundMethod] = useState<'money' | 'voucher' | 'replacement'>('money');

  useEffect(() => {
    if (isOpen) {
      dialogRef.current?.showModal();
    } else {
      dialogRef.current?.close();
    }
  }, [isOpen]);

  const formatAmount = (amount?: number, currency: string = 'USD') => {
    if (!amount) return 'N/A';
    return `${currency} ${amount.toFixed(2)}`;
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return 'Unknown date';
    }
  };

  const getStatusDisplay = (status: string) => {
    const statusMap = {
      'pending': { emoji: '⏳', text: 'Pending Review', className: 'bg-yellow-100 text-yellow-800' },
      'approved': { emoji: '✅', text: 'Approved', className: 'bg-green-100 text-green-800' },
      'rejected': { emoji: '❌', text: 'Rejected', className: 'bg-red-100 text-red-800' }
    };
    
    return statusMap[status as keyof typeof statusMap] || 
           { emoji: '❓', text: status, className: 'bg-gray-100 text-gray-800' };
  };

  const statusInfo = getStatusDisplay(refundData.status);

  const handleSubmit = async () => {
    if (!responseContent.trim()) {
      alert('Please provide a response reason');
      return;
    }

    if (decisionType === 'approval' && !refundAmount.trim()) {
      alert('Please provide a refund amount for approval');
      return;
    }

    const decision: RefundDecision = {
      response_type: decisionType,
      response_content: responseContent,
      ...(decisionType === 'approval' && {
        refund_amount: refundAmount,
        refund_method: refundMethod
      })
    };

    await onSubmitDecision(decision);
  };

  const isPendingCase = refundData.status === 'pending';

  return (
    <dialog ref={dialogRef} className="refund-response-modal max-w-3xl w-full" onClose={onClose}>
      <div className="modal-container">
        <div className="modal-header">
          <h2 className="modal-title">💰 Refund Response Details</h2>
          <button onClick={onClose} className="modal-close-btn">×</button>
        </div>

        <div className="modal-body">
          <div className="space-y-4">
            <div className="case-header">
              <div className="flex justify-between items-center mb-3">
                <div>
                  <h3 className="font-semibold text-green-800 text-lg">Refund Case #{refundData.refund_request_id}</h3>
                  <span className={`status-badge ${statusInfo.className}`}>
                    {statusInfo.emoji} {statusInfo.text}
                  </span>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-600">Created</div>
                  <div className="text-sm font-medium">{formatDate(refundData.created_at)}</div>
                </div>
              </div>
            </div>

            {refundData.eligibility && (
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-800 mb-3">Eligibility Assessment</h3>
                <div className={`flex items-center p-2 rounded ${refundData.eligibility.is_eligible ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  <span className="text-lg mr-2">{refundData.eligibility.is_eligible ? '✅' : '❌'}</span>
                  <span className="font-medium">
                    {refundData.eligibility.is_eligible ? 'Eligible for Refund' : 'Not Eligible for Refund'}
                  </span>
                </div>
                
                {refundData.eligibility.reasons.length > 0 && (
                  <div className="mt-3">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Assessment Reasons:</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {refundData.eligibility.reasons.map((reason, index) => (
                        <li key={index} className="flex items-center">
                          <span className="mr-2">•</span>
                          {reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {refundData.eligibility.calculated_refund_amount && (
                  <div className="mt-3 bg-blue-50 p-2 rounded">
                    <div className="text-sm text-gray-700">Calculated Amount:</div>
                    <div className="text-lg font-bold text-blue-700">
                      {formatAmount(refundData.eligibility.calculated_refund_amount)}
                    </div>
                  </div>
                )}
              </div>
            )}

            {refundData.refund_amount && (
              <div className="amount-display">
                <h3 className="font-semibold text-purple-800 mb-3">Approved Refund Amount</h3>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-700 mb-2">
                    {formatAmount(refundData.refund_amount.amount, refundData.refund_amount.currency)}
                  </div>
                  <div className="text-sm text-purple-600">Final approved refund amount</div>
                </div>
              </div>
            )}
            
            {refundData.product_ids.length > 0 && (
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-800 mb-3">Products Involved</h3>
                <div className="product-grid">
                  {refundData.product_ids.map((productId, index) => (
                    <div key={index} className="product-tag">
                      {productId}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {isPendingCase && (
              <div className="decision-section">
                <h3 className="font-semibold text-blue-800 mb-4 text-lg">🤔 Make Refund Decision</h3>
                
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Decision Type</label>
                  <div className="decision-type-buttons">
                    <button type="button" onClick={() => setDecisionType('approval')} className={`decision-btn approval ${decisionType === 'approval' ? 'selected' : ''}`}>
                      ✅ Approve
                    </button>
                    <button type="button" onClick={() => setDecisionType('rejection')} className={`decision-btn rejection ${decisionType === 'rejection' ? 'selected' : ''}`}>
                      ❌ Reject
                    </button>
                    <button type="button" onClick={() => setDecisionType('request_additional_evidence')} className={`decision-btn info-request ${decisionType === 'request_additional_evidence' ? 'selected' : ''}`}>
                      📝 Request Info
                    </button>
                  </div>
                </div>

                {decisionType === 'approval' && (
                  <div className="mb-4 space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Refund Amount</label>
                      <div className="amount-input-container">
                        <span className="currency-symbol">$</span>
                        <input type="number" value={refundAmount} onChange={(e) => setRefundAmount(e.target.value)} className="form-input text-right font-medium" placeholder="0.00" min="0" step="0.01" />
                        <span className="calculated-amount">Calculated: ${refundData.eligibility?.calculated_refund_amount?.toFixed(2) || 'N/A'}</span>
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Refund Method</label>
                      <select value={refundMethod} onChange={(e) => setRefundMethod(e.target.value as 'money' | 'voucher' | 'replacement')} className="form-input">
                        <option value="money">💰 Money Refund (Credit Card/Debit Card)</option>
                        <option value="voucher">🎟️ Store Credit Voucher (10% Bonus)</option>
                        <option value="replacement">🔄 Product Replacement</option>
                      </select>
                    </div>
                  </div>
                )}

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {decisionType === 'approval' ? 'Approval Reason' : 
                     decisionType === 'rejection' ? 'Rejection Reason' : 
                     'Information Request'}
                  </label>
                  <textarea value={responseContent} onChange={(e) => setResponseContent(e.target.value)} className="form-input form-textarea" placeholder={`Enter ${decisionType === 'approval' ? 'approval' : decisionType === 'rejection' ? 'rejection' : 'information request'} reason...`} />
                </div>
              </div>
            )}

            {refundData.decision_reason && (
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-800 mb-2">Decision Reason</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{refundData.decision_reason}</p>
              </div>
            )}

            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-800 mb-3">Case Timeline</h3>
              <div className="space-y-2 text-sm">
                <div className="timeline-item">
                  <span className="text-gray-600">Created:</span>
                  <span className="text-gray-800">{formatDate(refundData.created_at)}</span>
                </div>
                <div className="timeline-item">
                  <span className="text-gray-600">Last Updated:</span>
                  <span className="text-gray-800">{formatDate(refundData.updated_at)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

         {isPendingCase && (
           <div className="modal-actions">
             <div className="action-buttons">
               <button onClick={onClose} className="btn-cancel" disabled={isSubmitting}>
                 Cancel
               </button>
               <button onClick={handleSubmit} disabled={isSubmitting} className="btn-submit">
                 {isSubmitting ? 'Submitting...' : 
                   decisionType === 'approval' ? 'Approve Refund' : 
                   decisionType === 'rejection' ? 'Reject Refund' : 
                   'Request Information'}
               </button>
             </div>
           </div>
         )}
        
        {!isPendingCase && (
          <div className="modal-actions">
            <button onClick={onClose} className="btn btn-cancel">Close</button>
          </div>
        )}
      </div>
    </dialog>
  );
};

export default RefundResponseModal;