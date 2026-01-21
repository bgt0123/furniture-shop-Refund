import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { refundApi, supportApi, ApiError } from '../../services/api';

interface RefundCaseDetail {
  refund_case_id: string;
  case_number: string;
  customer_id: string;
  order_id: string;
  status: string;
  created_at: string;
  updated_at: string;
  request_reason: string;
  product_ids: string[];
  evidence_photos?: string[];
  support_case_details?: SupportCase;
  feedback_entries?: any[];
}

interface SupportCase {
  case_number: string;
  customer_id: string;
  case_type: string;
  subject: string;
  description: string;
  status: string;
  refund_request_id?: string;
  created_at: string;
  updated_at: string;
}

const RefundCaseDetail: React.FC = () => {
  const { refundCaseId } = useParams<{ refundCaseId: string }>();
  const [refundCase, setRefundCase] = useState<RefundCaseDetail | null>(null);
  const [supportCase, setSupportCase] = useState<SupportCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCaseDetails();
  }, [refundCaseId]);

  const fetchCaseDetails = async () => {
    if (!refundCaseId) return;

    try {
      setLoading(true);
      setError(null);

      // Fetch refund case details
      const caseData = await refundApi.getRefundCaseDetailed(refundCaseId);
      setRefundCase(caseData);

      // If there's an associated support case, fetch its details
      if (caseData.case_number) {
        try {
          const supportData = await supportApi.getSupportCase(caseData.case_number);
          setSupportCase(supportData);
        } catch (err) {
          console.error('Failed to fetch support case:', err);
        }
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to fetch refund case details');
    } finally {
      setLoading(false);
    }
  };

  const getStatusDisplay = (status: string) => {
    const statusMap = {
      'pending': { emoji: '⏳', text: 'Pending Review', className: 'bg-yellow-100 text-yellow-800' },
      'approved': { emoji: '✅', text: 'Approved', className: 'bg-green-100 text-green-800' },
      'rejected': { emoji: '❌', text: 'Rejected', className: 'bg-red-100 text-red-800' },
      'processing': { emoji: '🔄', text: 'Processing', className: 'bg-blue-100 text-blue-800' }
    };
    
    return statusMap[status as keyof typeof statusMap] || 
           { emoji: '❓', text: status, className: 'bg-gray-100 text-gray-800' };
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return 'Unknown date';
    }
  };

  // refreshCaseDetails function removed - using fetchCaseDetails directly

  if (loading) {
    return (
      <div className="detail-page min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 p-6">
        <div className="loading-spinner">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
          <p className="mt-2 text-gray-600">Loading refund case details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="detail-page min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="error-alert">
            {error}
          </div>
          <Link to="/refund-cases" className="back-link">
            ← Back to Refund Cases
          </Link>
        </div>
      </div>
    );
  }

  if (!refundCase) {
    return (
      <div className="detail-page min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-800 mb-4">Refund Case Not Found</h1>
            <p className="text-gray-600 mb-4">The requested refund case could not be found.</p>
            <Link to="/refund-cases" className="back-link">
              ← Back to Refund Cases
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const statusInfo = getStatusDisplay(refundCase.status);

  return (
    <div className="refund-case-detail detail-page min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="header-section">
          <Link to="/refund-cases" className="back-link">
            ← Back to Refund Cases
          </Link>
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                Refund Case #{refundCase.refund_case_id}
              </h1>
              <span className={`status-badge ${statusInfo.className.replace('bg-', 'status-')}`}>
                {statusInfo.emoji} {statusInfo.text}
              </span>
            </div>
          </div>
        </div>

        {/* Case Details */}
        <div className="content-card p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Refund Request Details</h2>
          
          <div className="info-grid">
            <div className="info-item">
              <div className="info-item-label">Refund Case ID</div>
              <div className="info-item-value">{refundCase.refund_case_id}</div>
            </div>
            <div className="info-item">
              <div className="info-item-label">Order ID</div>
              <div className="info-item-value">{refundCase.order_id}</div>
            </div>
            <div className="info-item">
              <div className="info-item-label">Customer ID</div>
              <div className="info-item-value">{refundCase.customer_id}</div>
            </div>
            <div className="info-item">
              <div className="info-item-label">Created</div>
              <div className="info-item-value">{formatDate(refundCase.created_at)}</div>
            </div>
            <div className="info-item">
              <div className="info-item-label">Last Updated</div>
              <div className="info-item-value">{formatDate(refundCase.updated_at)}</div>
            </div>
          </div>

          {/* Products */}
          {refundCase.product_ids.length > 0 && (
            <div className="mb-6">
              <h3 className="font-medium text-gray-700 mb-2">Products Involved</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {refundCase.product_ids.map((productId, index) => (
                  <div key={index} className="bg-gray-50 p-2 rounded">
                    <span className="text-gray-800">{productId}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Reason */}
          <div className="mb-6">
            <h3 className="font-medium text-gray-700 mb-2">Reason for Refund</h3>
            <p className="text-gray-800 whitespace-pre-wrap">{refundCase.request_reason}</p>
          </div>

          {/* Evidence */}
          {refundCase.evidence_photos && refundCase.evidence_photos.length > 0 && (
            <div className="mb-6">
              <h3 className="font-medium text-gray-700 mb-2">Evidence Photos</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {refundCase.evidence_photos.map((photo, index) => (
                  <div key={index} className="bg-gray-100 p-4 rounded-lg text-center">
                    <span className="text-gray-600">Photo {index + 1}</span>
                    <p className="text-sm text-gray-500 mt-1">{photo}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

           {/* Associated Support Case */}
           {refundCase.case_number && (
             <div className="border-t pt-4 mt-6">
               <h3 className="font-medium text-gray-700 mb-4">Associated Support Case</h3>
               {supportCase ? (
                 <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                   <div className="flex justify-between items-center">
                     <div>
                       <h4 className="font-semibold text-blue-800">
                         Support Case #{supportCase.case_number}
                       </h4>
                       <p className="text-blue-600 text-sm mb-1">
                         Subject: {supportCase.subject}
                       </p>
                       <p className="text-blue-600 text-sm">
                         Status: {supportCase.status}
                       </p>
                     </div>
                      <Link 
                        to={{
                          pathname: `/support-cases/${supportCase.case_number}`,
                          search: `?role=agent`
                        }}
                        className="btn-primary"
                      >
                        View Support Case
                      </Link>
                   </div>
                 </div>
               ) : (
                 <p className="text-gray-600">Support case details loading...</p>
               )}
             </div>
           )}

           {/* Feedback Section Removed */}
         </div>
      </div>
    </div>
  );
};

export default RefundCaseDetail;