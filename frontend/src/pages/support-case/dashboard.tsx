import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import SupportCaseForm from '../../components/support/support-case-form';
import { supportApi, refundApi, ApiError } from '../../services/api';

interface SupportCase {
  id: string;
  caseNumber: string;
  title: string;
  description: string;
  caseType: 'Question' | 'Refund';
  status: 'Open' | 'In Progress' | 'Closed';
  refund_request_id?: string;
  created: string;
  updated: string;
}

const SupportCaseDashboard: React.FC = () => {
  const [cases, setCases] = useState<SupportCase[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Mock customer ID - in real app this would come from authentication
  const mockCustomerId = 'cust-123';

  const [showModal, setShowModal] = useState(false);
  const [editingCase, setEditingCase] = useState<SupportCase | null>(null);

  // Fetch support cases on component mount
  useEffect(() => {
    fetchSupportCases();
  }, []);

  const fetchSupportCases = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching support cases for customer:', mockCustomerId);
      
      const fetchedCases = await supportApi.getCustomerSupportCases(mockCustomerId);
      console.log('Fetched cases:', fetchedCases);
      
      // Map API response to frontend format
      const mappedCases: SupportCase[] = fetchedCases.map(caseData => {
        let status: 'Open' | 'In Progress' | 'Closed';
        switch(caseData.status) {
          case 'closed': status = 'Closed'; break;
          case 'in_progress': status = 'In Progress'; break;
          default: status = 'Open';
        }
        
        let caseType: 'Question' | 'Refund';
        switch(caseData.case_type) {
          case 'refund': caseType = 'Refund'; break;
          default: caseType = 'Question';
        }
        
        return {
          id: caseData.case_number,
          caseNumber: caseData.case_number,
          title: caseData.subject,
          description: caseData.description,
          caseType,
          status,
          refund_request_id: caseData.refund_request_id,
          created: new Date(caseData.created_at).toISOString().split('T')[0],
          updated: new Date(caseData.updated_at).toLocaleDateString()
        };
      });
      
      setCases(mappedCases);
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : 'Failed to fetch support cases';
      setError(errorMessage);
      
      // Show empty state if backend is not available
      if (err instanceof ApiError && err.statusCode === 0) {
        setCases([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFormSubmit = async (formData: { title: string; description: string; caseType: 'Question' | 'Refund' }) => {
    try {
      setError(null);
      
      if (editingCase) {
         // Edit existing case - API doesn't support editing yet
         const updatedCases: SupportCase[] = cases.map(c => 
           c.id === editingCase.id 
             ? { ...c, title: formData.title, description: formData.description, caseType: formData.caseType }
             : c
         );
         setCases(updatedCases);
        setEditingCase(null);
       } else {
         // Create new case
         const newCaseData = await supportApi.createSupportCase({
           customer_id: mockCustomerId,
           case_type: formData.caseType.toLowerCase(),
           subject: formData.title,
           description: formData.description,
           refund_request_id: undefined,
           evidence_files: []
         });
         
         // If case type is Refund, create a refund request automatically
         if (formData.caseType === 'Refund') {
           try {
             // Create refund request linked to this support case
             const refundResponse = await refundApi.createRefundRequest({
               case_number: newCaseData.case_number,
               customer_id: mockCustomerId,
               order_id: 'ORD-' + Math.random().toString(36).substr(2, 8).toUpperCase(),
               product_ids: ['PROD-001', 'PROD-002'],
               request_reason: 'Product defect or damage',
               evidence_photos: []
             });
             
             // Update support case to link the refund request
             await supportApi.updateCaseType(newCaseData.case_number, 'refund', refundResponse.refund_case_id);
             
             // Map API response to frontend format with refund request linked
             let status: 'Open' | 'In Progress' | 'Closed';
             switch(newCaseData.status) {
               case 'closed': status = 'Closed'; break;
               case 'in_progress': status = 'In Progress'; break;
               default: status = 'Open';
             }
             
             const newCase: SupportCase = {
               id: newCaseData.case_number,
               caseNumber: newCaseData.case_number,
               title: newCaseData.subject,
               description: newCaseData.description,
               caseType: 'Refund',
               status,
               refund_request_id: refundResponse.refund_case_id,
               created: new Date(newCaseData.created_at).toISOString().split('T')[0],
               updated: 'just now'
             };
             
             setCases([newCase, ...cases]);
           } catch (err) {
             // If refund creation fails, still create the support case but show error
             console.error('Failed to create refund request:', err);
             
             let status: 'Open' | 'In Progress' | 'Closed';
             switch(newCaseData.status) {
               case 'closed': status = 'Closed'; break;
               case 'in_progress': status = 'In Progress'; break;
               default: status = 'Open';
             }
             
             let caseType: 'Question' | 'Refund';
             switch(newCaseData.case_type) {
               case 'refund': caseType = 'Refund'; break;
               default: caseType = 'Question';
             }
             
             const newCase: SupportCase = {
               id: newCaseData.case_number,
               caseNumber: newCaseData.case_number,
               title: newCaseData.subject,
               description: newCaseData.description,
               caseType,
               status,
               created: new Date(newCaseData.created_at).toISOString().split('T')[0],
               updated: 'just now'
             };
             
             setCases([newCase, ...cases]);
             setError('Support case created but refund request failed. Please create refund request manually.');
           }
         } else {
           // Normal case creation for Question type
           let status: 'Open' | 'In Progress' | 'Closed';
           switch(newCaseData.status) {
             case 'closed': status = 'Closed'; break;
             case 'in_progress': status = 'In Progress'; break;
             default: status = 'Open';
           }
           
           let caseType: 'Question' | 'Refund';
           switch(newCaseData.case_type) {
             case 'refund': caseType = 'Refund'; break;
             default: caseType = 'Question';
           }
           
           const newCase: SupportCase = {
             id: newCaseData.case_number,
             caseNumber: newCaseData.case_number,
             title: newCaseData.subject,
             description: newCaseData.description,
             caseType,
             status,
             created: new Date(newCaseData.created_at).toISOString().split('T')[0],
             updated: 'just now'
           };
           
           setCases([newCase, ...cases]);
         }
       }
      setShowModal(false);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to save support case');
    }
  };

  const handleCloseCase = async (caseId: string) => {
    try {
      setError(null);
      
      // Find the case number from the case ID
      const caseToClose = cases.find(c => c.id === caseId);
      if (!caseToClose) return;
      
      await supportApi.closeCase(caseToClose.caseNumber);
      
      // Update local state immediately for better UX
      const updatedCases = cases.map(c => 
        c.id === caseId && c.status !== 'Closed' 
          ? { ...c, status: 'Closed' as const }
          : c
      );
      setCases(updatedCases);
      
      // Refresh the cases list to get updated status (to sync with backend)
      fetchSupportCases();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to close support case');
    }
  };

  const handleReopenCase = async (caseId: string) => {
    try {
      setError(null);
      
      // Find the case number from the case ID
      const caseToReopen = cases.find(c => c.id === caseId);
      if (!caseToReopen) return;
      
      try {
        // Try to call the backend endpoint
        await supportApi.reopenCase(caseToReopen.caseNumber);
        
        // Update local state immediately for better UX
        const updatedCases = cases.map(c => 
          c.id === caseId && c.status === 'Closed' 
            ? { ...c, status: 'Open' as const }
            : c
        );
        setCases(updatedCases);
      } catch (err) {
        if (err instanceof ApiError && err.statusCode === 404) {
          // If endpoint doesn't exist yet, simulate reopening
          const updatedCases = cases.map(c => 
            c.id === caseId && c.status === 'Closed' 
              ? { ...c, status: 'Open' as const }
              : c
          );
          setCases(updatedCases);
          return;
        }
        throw err;
      }
      
      // Refresh the cases list to get updated status (to sync with backend)
      fetchSupportCases();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to reopen support case');
    }
  };

  const handleCreateRefundRequest = async (caseId: string) => {
    try {
      setError(null);
      
      // Find the case number from the case ID
      const caseToRefund = cases.find(c => c.id === caseId);
      if (!caseToRefund) {
        setError('Support case not found');
        return;
      }
      
      // Validate that this is a Question case that can be converted to Refund
      if (caseToRefund.caseType !== 'Question') {
        setError('Cannot create refund request for non-question cases');
        return;
      }
      
      if (caseToRefund.status === 'Closed') {
        setError('Cannot create refund request for closed cases');
        return;
      }
      
      if (caseToRefund.refund_request_id) {
        setError('This case already has a refund request');
        return;
      }
      
      const refundResponse = await refundApi.createRefundRequest({
        case_number: caseToRefund.caseNumber,
        customer_id: mockCustomerId,
        order_id: 'ORD-' + Math.random().toString(36).substr(2, 8).toUpperCase(),
        product_ids: ['PROD-001', 'PROD-002'],
        request_reason: 'Product defect or damage',
        evidence_photos: []
      });
      
      try {
        // Update support case to refund type and link the refund request
        await supportApi.updateCaseType(caseToRefund.caseNumber, 'refund', refundResponse.refund_case_id);
      } catch (err) {
        if (err instanceof ApiError && err.statusCode === 404) {
           // If endpoint doesn't exist yet, simulate the update
           const updatedCases = cases.map(c => 
             c.id === caseId && c.caseType === 'Question' && !c.refund_request_id
               ? { 
                   ...c, 
                   caseType: 'Refund' as const, 
                   refund_request_id: refundResponse.refund_case_id 
                 }
               : c
           );
           setCases(updatedCases);
          return;
        }
        throw err;
      }
      
      // Refresh the cases list to get updated status
      fetchSupportCases();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to create refund request');
    }
  };

  const startEditingCase = (supportCase: SupportCase) => {
    setEditingCase(supportCase);
    setShowModal(true);
  };

  const handleModalClose = () => {
    setShowModal(false);
    setEditingCase(null);
  };

  const startCreatingCase = () => {
    console.log('Create button clicked');
    setEditingCase(null);
    setShowModal(true);
  };

  return (
    <div className="support-case-dashboard min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6 app relative z-10">
      <div className="max-w-6xl mx-auto support-dashboard">
        <div className="header-section mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            📋 Support Case Dashboard
          </h1>
          <p className="text-gray-600 text-lg">
            Manage your support cases and create refund requests
          </p>
        </div>

        <SupportCaseForm
          isOpen={showModal}
          onClose={handleModalClose}
          onSubmit={handleFormSubmit}
          onRefundRequestCreate={handleCreateRefundRequest}
          editingCase={editingCase}
        />

        {error && (
          <div className="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 gap-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold text-gray-800">
                My Support Cases
              </h2>
              <button
                onClick={startCreatingCase}
                disabled={loading}
                className="btn-primary px-6 py-3 text-lg flex items-center disabled:opacity-50"
              >
                <span className="mr-2">➕</span>
                {loading ? 'Loading...' : 'Create New Case'}
              </button>
            </div>

            {loading ? (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="mt-2 text-gray-600">Loading support cases...</p>
              </div>
            ) : cases.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-600">No support cases found.</p>
              </div>
            ) : (
              <div className="case-list space-y-4">
                {cases.map((supportCase) => (
                  <div key={supportCase.id} className="case-item bg-gradient-to-r from-white to-blue-50 border-l-4 border-blue-500 p-4 rounded-lg shadow-sm hover:shadow-md transition-all duration-300 case-card">
                    <div className="flex justify-between items-center mb-2 gap-4">
                      <span className="case-number font-mono text-sm text-gray-600 flex-1 mr-2">
                        {supportCase.caseNumber}
                      </span>
                      <span className={`status px-3 py-1 rounded-full text-sm font-medium flex-shrink-0 ml-2 ${
                        supportCase.status === 'Open' ? 'bg-green-100 text-green-800' :
                        supportCase.status === 'In Progress' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {supportCase.status === 'Open' && '✅ '}
                        {supportCase.status === 'In Progress' && '⏳ '}
                        {supportCase.status === 'Closed' && '🔒 '}
                        {supportCase.status}
                      </span>
                    </div>
                    <h3 className="text-lg font-medium text-gray-800 mb-2">
                      {supportCase.title}
                    </h3>
                    <p className="text-gray-600 text-sm mb-3">
                      {supportCase.description}
                    </p>
                    <div className="flex space-x-2 mb-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        supportCase.caseType === 'Refund' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                      }`}>
                        {supportCase.caseType} Case
                      </span>
                    </div>
                     <div className="grid grid-cols-1 gap-2 text-xs text-gray-500 mb-4">
                       <div><span className="font-medium">Created:</span> {supportCase.created}</div>
                       <div><span className="font-medium">Last updated:</span> {supportCase.updated}</div>
                     </div>
                       <div className="action-buttons">
                         <Link 
                           to={`/support-cases/${supportCase.caseNumber}`}
                           className="btn-primary"
                         >
                           📋 View Details
                         </Link>
                        {supportCase.status !== 'Closed' && (
                         <button
                           onClick={() => startEditingCase(supportCase)}
                           className="btn-secondary"
                         >
                           ✏️ Edit
                         </button>
                        )}
                        {supportCase.refund_request_id && (
                         <Link
                           to={`/refund-cases/${supportCase.refund_request_id}`}
                           className="btn-primary"
                         >
                           💰 View Refund Case
                         </Link>
                        )}
                        {!supportCase.refund_request_id && supportCase.caseType === 'Refund' && supportCase.status !== 'Closed' && (
                          <span className="refund-status-message text-xs">
                            Case already configured for refund
                          </span>
                        )}
                         {supportCase.status === 'Closed' ? (
                           <button
                             onClick={() => handleReopenCase(supportCase.id)}
                             className="btn-warning"
                           >
                             🔄 Reopen Case
                           </button>
                         ) : (
                           <button
                             onClick={() => handleCloseCase(supportCase.id)}
                             className="btn-danger"
                           >
                             🔒 Close Case
                           </button>
                         )}
                      </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SupportCaseDashboard;