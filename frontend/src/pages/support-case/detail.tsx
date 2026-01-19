import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { supportApi, refundApi, ApiError } from '../../services/api';

interface SupportCaseDetail {
  case_number: string;
  customer_id: string;
  case_type: string;
  subject: string;
  description: string;
  status: string;
  refund_request_id?: string;
  assigned_agent_id?: string;
  created_at: string;
  updated_at: string;
  responses?: SupportResponse[];
  attachments?: string[];
}

interface SupportResponse {
  id: string;
  sender_id: string;
  sender_type: string;
  content: string;
  message_type: string;
  attachments?: string[];
  is_internal?: boolean;
  created_at: string;
}

interface RefundCase {
  refund_case_id: string;
  case_number: string;
  customer_id: string;
  order_id: string;
  status: string;
  created_at: string;
  updated_at: string;
}

const SupportCaseDetail: React.FC = () => {
  const { caseNumber } = useParams<{ caseNumber: string }>();
  const [supportCase, setSupportCase] = useState<SupportCaseDetail | null>(null);
  const [refundCase, setRefundCase] = useState<RefundCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCaseDetails();
  }, [caseNumber]);

  const fetchCaseDetails = async () => {
    if (!caseNumber) return;

    try {
      setLoading(true);
      setError(null);

      // Fetch support case details
      const caseData = await supportApi.getSupportCaseDetailed(caseNumber);
      setSupportCase(caseData);

      // If there's a refund request ID, fetch refund case details
      if (caseData.refund_request_id) {
        try {
          const refundData = await refundApi.getRefundCase(caseData.refund_request_id);
          setRefundCase(refundData);
        } catch (err) {
          console.error('Failed to fetch refund case:', err);
        }
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to fetch case details');
    } finally {
      setLoading(false);
    }
  };

  const getStatusDisplay = (status: string) => {
    const statusMap = {
      'open': { emoji: '✅', text: 'Open', className: 'bg-green-100 text-green-800' },
      'in_progress': { emoji: '⏳', text: 'In Progress', className: 'bg-yellow-100 text-yellow-800' },
      'closed': { emoji: '🔒', text: 'Closed', className: 'bg-gray-100 text-gray-800' }
    };
    
    return statusMap[status as keyof typeof statusMap] || 
           { emoji: '❓', text: status, className: 'bg-gray-100 text-gray-800' };
  };

  const getCaseTypeDisplay = (caseType: string) => {
    const typeMap = {
      'question': { emoji: '❓', text: 'General Question', className: 'bg-blue-100 text-blue-800' },
      'refund': { emoji: '💰', text: 'Refund Request', className: 'bg-green-100 text-green-800' }
    };
    
    return typeMap[caseType as keyof typeof typeMap] || 
           { emoji: '📋', text: caseType, className: 'bg-gray-100 text-gray-800' };
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return 'Unknown date';
    }
  };

  if (loading) {
    return (
      <div className="support-case-detail detail-page min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
        <div className="loading-spinner">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Loading case details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="support-case-detail detail-page min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="error-alert">
            {error}
          </div>
          <Link to="/support-cases" className="back-link">
            ← Back to Support Cases
          </Link>
        </div>
      </div>
    );
  }

  if (!supportCase) {
    return (
      <div className="support-case-detail detail-page min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-800 mb-4">Case Not Found</h1>
            <p className="text-gray-600 mb-4">The requested support case could not be found.</p>
            <Link to="/support-cases" className="back-link">
              ← Back to Support Cases
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const statusInfo = getStatusDisplay(supportCase.status);
  const typeInfo = getCaseTypeDisplay(supportCase.case_type);

  return (
    <div className="support-case-detail detail-page min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="header-section">
          <Link to="/support-cases" className="back-link">
            ← Back to Support Cases
          </Link>
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                Support Case #{supportCase.case_number}
              </h1>
              <span className={`status-badge ${statusInfo.className.replace('bg-', 'status-')}`}>
                {statusInfo.emoji} {statusInfo.text}
              </span>
            </div>
            <span className={`status-badge ${typeInfo.className.replace('bg-', 'status-')}`}>
              {typeInfo.emoji} {typeInfo.text}
            </span>
          </div>
        </div>

        {/* Case Details */}
        <div className="content-card p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Case Details</h2>
          
          <div className="info-grid">
            <div className="info-item">
              <div className="info-item-label">Subject</div>
              <div className="info-item-value">{supportCase.subject}</div>
            </div>
            <div className="info-item">
              <div className="info-item-label">Customer ID</div>
              <div className="info-item-value">{supportCase.customer_id}</div>
            </div>
            <div className="info-item">
              <div className="info-item-label">Created</div>
              <div className="info-item-value">{formatDate(supportCase.created_at)}</div>
            </div>
            <div className="info-item">
              <div className="info-item-label">Last Updated</div>
              <div className="info-item-value">{formatDate(supportCase.updated_at)}</div>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="font-medium text-gray-700 mb-2">Description</h3>
            <p className="text-gray-800 whitespace-pre-wrap">{supportCase.description}</p>
          </div>

          {/* Associated Refund Case */}
          {supportCase.refund_request_id && (
            <div className="border-t pt-4 mt-6">
              <h3 className="font-medium text-gray-700 mb-4">Associated Refund Case</h3>
              {refundCase ? (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <h4 className="font-semibold text-green-800">
                        Refund Case #{refundCase.refund_case_id}
                      </h4>
                      <p className="text-green-600 text-sm">
                        Status: {refundCase.status}
                      </p>
                    </div>
                    <Link 
                      to={`/refund-cases/${refundCase.refund_case_id}`}
                      className="btn-primary"
                    >
                      View Refund Case
                    </Link>
                  </div>
                </div>
              ) : (
                <p className="text-gray-600">Refund case details loading...</p>
              )}
            </div>
          )}

          {/* Attachments */}
          {supportCase.attachments && supportCase.attachments.length > 0 && (
            <div className="border-t pt-4 mt-6">
              <h3 className="font-medium text-gray-700 mb-4">Attachments</h3>
              <div className="space-y-2">
                {supportCase.attachments.map((attachment, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                    <span className="text-gray-600">{attachment}</span>
                    <button className="text-blue-600 hover:text-blue-800 text-sm">
                      Download
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Responses Section */}
        {supportCase.responses && supportCase.responses.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Case Responses</h2>
            <div className="space-y-4">
              {supportCase.responses.map((response) => (
                <div key={response.id} className="border-l-4 border-blue-500 pl-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium text-gray-700">
                      {response.sender_type === 'agent' ? '👤 Support Agent' : '👤 Customer'}
                    </span>
                    <span className="text-xs text-gray-500">
                      {formatDate(response.created_at)}
                    </span>
                  </div>
                  <p className="text-gray-800 whitespace-pre-wrap">{response.content}</p>
                  {response.attachments && response.attachments.length > 0 && (
                    <div className="mt-2">
                      <span className="text-xs text-gray-600">Attachments: </span>
                      {response.attachments.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SupportCaseDetail;