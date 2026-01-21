import React, { useState, useEffect } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { supportApi, refundApi, ApiError } from '../../services/api';
import CustomerCommentModal from '../../components/support/customer-comment-modal';
import AgentCommentModal from '../../components/support/agent-comment-modal';

interface SupportCaseDetail {
  case_number: string;
  customer_id: string;
  case_type: string;
  subject: string;
  description: string;
  status: string;
  refund_request_ids?: string[];
  assigned_agent_id?: string;
  order_id?: string;
  product_ids?: string[];
  delivery_date?: string;
  comments?: any[];
  created_at: string;
  updated_at: string;
  attachments?: string[];
}

// SupportResponse interface removed - using Comment system instead

interface RefundCase {
  refund_case_id: string;
  case_number: string;
  customer_id: string;
  order_id: string;
  status: string;
  created_at: string;
  updated_at: string;
  request_reason?: string;
  product_ids?: string[];
}

const SupportCaseDetail: React.FC = () => {
  const { caseNumber } = useParams<{ caseNumber: string }>();
  const location = useLocation();
   const [supportCase, setSupportCase] = useState<SupportCaseDetail | null>(null);
   const [refundCases, setRefundCases] = useState<RefundCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCustomerCommentModal, setShowCustomerCommentModal] = useState(false);
  const [showAgentCommentModal, setShowAgentCommentModal] = useState(false);
  
  // Get user role from URL query parameter, default to 'customer' for safety
  const urlParams = new URLSearchParams(location.search);
  const userRoleParam = urlParams.get('role');
  const [currentUser] = useState({
    id: 'detail-viewer',
    role: (userRoleParam as 'customer' | 'agent' | 'admin') || 'customer',
    name: userRoleParam === 'agent' ? 'Agent' : 'Customer'
  });

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

         // If there are refund request IDs, fetch refund case details
         if (caseData.refund_request_ids && caseData.refund_request_ids.length > 0) {
           const refundPromises = caseData.refund_request_ids.map(async (refundRequestId: string) => {
             try {
               return await refundApi.getRefundCaseDetailed(refundRequestId);
             } catch (err) {
               console.error('Failed to fetch refund case:', err);
               // Set a dummy refund case with 'pending' status
               return {
                 refund_case_id: refundRequestId,
                 case_number: caseData.case_number,
                 customer_id: caseData.customer_id,
                 order_id: caseData.order_id || 'ORD-unknown',
                 status: 'pending',
                 created_at: caseData.created_at,
                 updated_at: caseData.updated_at,
                 request_reason: 'Refund request',
                 product_ids: caseData.product_ids || []
               } as RefundCase;
             }
           });
           
           const refundResults = await Promise.all(refundPromises);
           setRefundCases(refundResults.filter(Boolean));
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

   const getRefundStatusDisplay = (status: string) => {
     const statusMap = {
       'pending': { emoji: '⏳', text: 'Pending Review', className: 'bg-yellow-100 text-yellow-800' },
       'approved': { emoji: '✅', text: 'Approved', className: 'bg-green-100 text-green-800' },
       'rejected': { emoji: '❌', text: 'Rejected', className: 'bg-red-100 text-red-800' }
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

  const handleCustomerCommentSubmit = async (content: string, files?: File[]) => {
    if (!supportCase) return;
    
    try {
      setError(null);
      
      // Upload files if any
      let uploadedAttachments: string[] = [];
      
      if (files && files.length > 0) {
        // For now, we'll just use the file names as mock attachments
        uploadedAttachments = files.map(file => file.name);
        // TODO: Implement actual file upload
      }

      const commentData = {
        author_id: currentUser.id,
        author_type: 'customer',
        content: content,
        comment_type: 'customer_comment',
        attachments: uploadedAttachments.length > 0 ? uploadedAttachments : undefined,
        is_internal: false
      };

      await supportApi.addComment(supportCase.case_number, commentData);
      
      // Refresh case details to show updated comments
      fetchCaseDetails();
      setShowCustomerCommentModal(false);
      
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to add comment');
    }
  };

  const handleAgentCommentSubmit = async (content: string, _commentType?: string, isInternal?: boolean, files?: File[], shouldCloseCase?: boolean) => {
    if (!supportCase) return;
    
    try {
      setError(null);
      
      // Upload files if any
      let uploadedAttachments: string[] = [];
      
      if (files && files.length > 0) {
        // For now, we'll just use the file names as mock attachments
        uploadedAttachments = files.map(file => file.name);
        // TODO: Implement actual file upload
      }

      const commentData = {
        author_id: currentUser.id,
        author_type: 'agent',
        content: content,
        comment_type: 'agent_response', // Using commentType parameter would require backend changes
        attachments: uploadedAttachments.length > 0 ? uploadedAttachments : undefined,
        is_internal: isInternal || false
      };

      await supportApi.addComment(supportCase.case_number, commentData);
      
      // If should close case and allowed to do so
      if (shouldCloseCase && supportCase.status !== 'closed') {
        try {
          await supportApi.closeCase(supportCase.case_number);
        } catch (err) {
          console.warn('Failed to close case after adding comment:', err);
        }
      }
      
      // Refresh case details to show updated comments
      fetchCaseDetails();
      setShowAgentCommentModal(false);
      
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to add comment');
    }
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
           <Link to={"/support-cases?role=" + currentUser.role} className="back-link">
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
           <Link to={"/support-cases?role=" + currentUser.role} className="back-link">
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
          <Link to={"/support-cases?role=" + currentUser.role} className="back-link">
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
            {supportCase.assigned_agent_id && (
              <div className="info-item">
                <div className="info-item-label">Assigned Agent</div>
                <div className="info-item-value">{supportCase.assigned_agent_id}</div>
              </div>
            )}
            {supportCase.order_id && (
              <div className="info-item">
                <div className="info-item-label">Order ID</div>
                <div className="info-item-value">{supportCase.order_id}</div>
              </div>
            )}
            {supportCase.product_ids && supportCase.product_ids.length > 0 && (
              <div className="info-item">
                <div className="info-item-label">Products</div>
                <div className="info-item-value">{supportCase.product_ids.join(', ')}</div>
              </div>
            )}
            {supportCase.delivery_date && (
              <div className="info-item">
                <div className="info-item-label">Delivery Date</div>
                <div className="info-item-value">{formatDate(supportCase.delivery_date)}</div>
              </div>
            )}
          </div>

          <div className="mb-6">
            <h3 className="font-medium text-gray-700 mb-2">Description</h3>
            <p className="text-gray-800 whitespace-pre-wrap">{supportCase.description}</p>
          </div>

          {/* Associated Refund Case */}
           {supportCase.refund_request_ids && supportCase.refund_request_ids.length > 0 && (
             <div className="border-t pt-4 mt-6">
               <h3 className="font-medium text-gray-700 mb-4">
                 Refund Request{supportCase.refund_request_ids.length > 1 ? 's' : ''} Details 
                 <span className="text-sm text-gray-500 font-normal">({supportCase.refund_request_ids.length} total)</span>
               </h3>
               {refundCases.length > 0 ? (
                 <div className="space-y-4">
                   {refundCases.map((refundCase, index) => (
                     <div key={refundCase.refund_case_id} className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-4">
                       <div className="flex justify-between items-start mb-3">
                         <div>
                           <h4 className="font-semibold text-green-800 text-lg">
                             💰 Refund Request #{index + 1}: {refundCase.refund_case_id}
                           </h4>
                           <div className="flex items-center mt-2">
                             {refundCase.status ? (
                               (() => {
                                 const statusInfo = getRefundStatusDisplay(refundCase.status);
                                 return (
                                   <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusInfo.className}`}>
                                     {statusInfo.emoji} {statusInfo.text}
                                   </span>
                                 );
                               })()
                             ) : (
                               <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                                 ❓ Status Unknown
                               </span>
                             )}
                           </div>
                         </div>
                         <Link 
                           to={`/refund-cases/${refundCase.refund_case_id}`}
                           className="btn-primary flex items-center"
                         >
                           📋 View Full Details
                         </Link>
                       </div>
                       <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                         <div className="bg-white p-2 rounded border">
                           <span className="font-medium text-gray-600">Order ID:</span>
                           <div className="text-gray-800 font-mono">{refundCase.order_id}</div>
                         </div>
                         <div className="bg-white p-2 rounded border">
                           <span className="font-medium text-gray-600">Created:</span>
                           <div className="text-gray-800">{formatDate(refundCase.created_at)}</div>
                         </div>
                         <div className="bg-white p-2 rounded border">
                           <span className="font-medium text-gray-600">Last Updated:</span>
                           <div className="text-gray-800">{formatDate(refundCase.updated_at)}</div>
                         </div>
                       </div>
                       {refundCase.request_reason && (
                         <div className="mt-3 bg-white p-2 rounded border">
                           <span className="font-medium text-gray-600">Reason:</span>
                           <div className="text-gray-800 text-sm">{refundCase.request_reason}</div>
                         </div>
                       )}
                     </div>
                   ))}
                 </div>
               ) : (
                 <div className="text-center py-4">
                   <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                   <p className="text-gray-600 mt-2">Loading refund case details...</p>
                 </div>
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

        {/* Comments Section */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Case History</h2>
          <div className="space-y-6">
             {supportCase.comments && supportCase.comments.length > 0 ? (
               <div className="space-y-4">
                
                {supportCase.comments && supportCase.comments.map((comment) => {
                  const getBorderColor = () => {
                    switch (comment.comment_type) {
                      case 'customer_comment': return 'border-blue-500';
                      case 'agent_response': return 'border-green-500';
                      case 'refund_feedback': return 'border-purple-500';
                      default: return 'border-gray-500';
                    }
                  };
                  
                  const getIcon = () => {
                    switch (comment.comment_type) {
                       case 'customer_comment': return '💬 Customer Comment';
                       case 'agent_response': return '🛠️ Agent Response';
                      case 'refund_feedback': return '💰 Refund Feedback';
                      default: return '📝 Comment';
                    }
                  };
                  
                  return (
                    <div key={comment.comment_id} className={`border-l-4 ${getBorderColor()} pl-4`}>
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-gray-700">
                          {getIcon()}
                        </span>
                        <span className="text-xs text-gray-500">
                          {formatDate(comment.timestamp)}
                        </span>
                      </div>
                      <p className="text-gray-800 whitespace-pre-wrap">{comment.content}</p>
                      {comment.attachments && comment.attachments.length > 0 && (
                        <div className="mt-2">
                          <span className="text-xs text-gray-600">Attachments: </span>
                          {comment.attachments.join(', ')}
                        </div>
                      )}
                      {comment.is_internal && (
                        <div className="mt-1">
                          <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">Internal Note</span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-gray-500 italic">No comments or responses yet.</p>
            )}
            
            {/* Add Comment Button */}
            {supportCase.status !== 'closed' && (
              <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
                <button
                  onClick={() => {
                    if (currentUser.role === 'agent') {
                      setShowAgentCommentModal(true);
                    } else {
                      setShowCustomerCommentModal(true);
                    }
                  }}
                  className="btn-primary"
                >
                  💬 Add Comment
                </button>
              </div>
            )}
          </div>
        </div>

        {currentUser.role === 'agent' ? (
          <AgentCommentModal
            isOpen={showAgentCommentModal}
            onClose={() => setShowAgentCommentModal(false)}
            onSubmit={handleAgentCommentSubmit}
            caseNumber={supportCase?.case_number || ''}
            allowCloseCase={true}
            currentStatus={supportCase?.status || 'open'}
          />
        ) : (
          <CustomerCommentModal
            isOpen={showCustomerCommentModal}
            onClose={() => setShowCustomerCommentModal(false)}
            onSubmit={handleCustomerCommentSubmit}
            caseNumber={supportCase?.case_number || ''}
          />
        )}
      </div>
    </div>
  );
};

export default SupportCaseDetail;