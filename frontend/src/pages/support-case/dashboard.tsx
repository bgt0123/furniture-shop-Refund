import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
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
  refund_status?: string;
  created: string;
  updated: string;
}

  const SupportCaseDashboard: React.FC = () => {
   const [cases, setCases] = useState<SupportCase[]>([]);
   const [loading, setLoading] = useState(false);
   const [error, setError] = useState<string | null>(null);
   const casesRef = useRef(cases);
   const isFetchingRefundStatuses = useRef(false);
   const location = useLocation();

   // Get user role from URL query parameter, default to 'customer' for safety
   const urlParams = new URLSearchParams(location.search);
   const userRoleParam = urlParams.get('role');

    // Mock user authentication - in real app this would come from authentication context
      const [currentUser, setCurrentUser] = useState({
        id: 'cust-123',
        role: (userRoleParam as 'customer' | 'agent' | 'admin') || 'customer',
        name: 'Demo Customer'
      });

   const [showModal, setShowModal] = useState(false);
   const [editingCase, setEditingCase] = useState<SupportCase | null>(null);

   // Fetch support cases on component mount and when user changes
   useEffect(() => {
     fetchSupportCases();
     
      // Set up polling for refund status updates every 5 seconds
       const intervalId = setInterval(() => {
         // Refresh refund statuses using ref to avoid dependency issues
         const refundCases = casesRef.current.filter(supportCase => supportCase.refund_request_id);
         console.log('🔁 Polling: Found', refundCases.length, 'refund cases to check');
         console.log('🔁 Polling: Cases with IDs:', refundCases.map(c => ({ caseNumber: c.caseNumber, refundId: c.refund_request_id, currentStatus: c.refund_status })));
         if (refundCases.length > 0) {
           console.log('🔁 Polling: Starting fetchRefundStatuses...');
           fetchRefundStatuses(refundCases);
         } else {
           console.log('🔁 Polling: No refund cases found');
         }
       }, 5000);
     
     return () => clearInterval(intervalId);
   }, [currentUser.id]);

   const fetchSupportCases = async () => {
     try {
       setLoading(true);
       setError(null);
        console.log('Fetching support cases for user:', currentUser.id);
       
       let fetchedCases: any[] = [];
       
       // Try to fetch from API first
       try {
          // Fetch cases based on user role
          if (currentUser.role === 'customer') {
            fetchedCases = await supportApi.getCustomerSupportCases(currentUser.id);
          } else {
            // For agents, fetch all cases
            fetchedCases = await supportApi.getAllSupportCases();
          }
         console.log('✅ API call successful. Fetched cases:', fetchedCases);
         
          // Save cases to localStorage for persistence
          if (fetchedCases.length > 0) {
            localStorage.setItem(`support-cases-${currentUser.id}`, JSON.stringify(fetchedCases));
          }
       } catch (error) {
         console.error('❌ Failed to fetch cases from API:', error);
         
         // Try to load from localStorage as fallback
          const storedCases = localStorage.getItem(`support-cases-${currentUser.id}`);
         if (storedCases) {
           fetchedCases = JSON.parse(storedCases);
           console.log('📁 Loaded cases from localStorage:', fetchedCases);
         } else {
           console.log('💡 No cases found, starting with empty list');
           fetchedCases = [];
         }
       }
      
        // Map API response to frontend format (if loaded from API)
        if (fetchedCases.length > 0 && fetchedCases[0].case_number) {
          // Create mapped cases first
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
              refund_status: undefined, // Will be fetched separately
              created: new Date(caseData.created_at).toISOString().split('T')[0],
              updated: new Date(caseData.updated_at).toLocaleDateString()
            };
          });
          
           setCases(mappedCases);
           casesRef.current = mappedCases;
           
           // Fetch refund statuses for refund cases separately (non-blocking)
           const refundCases = mappedCases.filter(supportCase => supportCase.refund_request_id);
           console.log('Found', refundCases.length, 'refund cases to fetch statuses for');
           if (refundCases.length > 0) {
             console.log('Calling fetchRefundStatuses with:', refundCases.map(c => c.caseNumber));
             fetchRefundStatuses(refundCases);
           }
          } else {
            // Already in correct format (loaded from localStorage)
            setCases(fetchedCases);
            casesRef.current = fetchedCases;
            
            // Fetch updated refund statuses for localStorage cases as well
            const refundCases = fetchedCases.filter(supportCase => supportCase.refund_request_id);
            console.log('Fetching refund statuses for localStorage cases:', refundCases.length);
            if (refundCases.length > 0) {
              console.log('Calling fetchRefundStatuses for localStorage cases:', refundCases.map(c => c.caseNumber));
              fetchRefundStatuses(refundCases);
            }
          }
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : 'Failed to fetch support cases';
      setError(errorMessage);
      
      // Show empty state if backend is not available
      if (err instanceof ApiError && err.statusCode === 0) {
        setCases([]);
        casesRef.current = [];
      }
    } finally {
      setLoading(false);
     }
   };

    const fetchRefundStatuses = async (refundCases: SupportCase[]) => {
      // Prevent overlapping calls
      if (isFetchingRefundStatuses.current) {
        console.log('Skipping refund status fetch - already in progress');
        return;
      }
      
      isFetchingRefundStatuses.current = true;
      console.log('fetchRefundStatuses called with:', refundCases.length, 'cases');
      try {
       const refundStatusPromises = refundCases.map(async (supportCase) => {
          try {
            console.log('Attempting to fetch refund status for:', supportCase.caseNumber, 'refund ID:', supportCase.refund_request_id);
            const refundData = await refundApi.getRefundCaseDetailed(supportCase.refund_request_id!);
            console.log('✅ Refund status fetched successfully for', supportCase.caseNumber, ':', refundData.status);
            console.log('Refund data details - ID:', refundData.refund_case_id, 'Status:', refundData.status, 'Case:', refundData.case_number);
            return {
              caseId: supportCase.id,
              refundStatus: refundData.status
            };
          } catch (error) {
            console.error('❌ Failed to fetch refund status for', supportCase.caseNumber, 'refund ID:', supportCase.refund_request_id, 'Error:', error);
            return {
              caseId: supportCase.id,
              refundStatus: 'unknown'
            };
          }
       });
       
        const refundStatusResults = await Promise.allSettled(refundStatusPromises);
        console.log('Refund status fetch completed. Results:', refundStatusResults.length);
        
        // Update cases with refund statuses
        setCases(currentCases => {
          console.log('Updating cases with refund statuses. Current cases:', currentCases.length);
          const updatedCases = currentCases.map(caseData => {
            const statusResult = refundStatusResults.find(result => 
              result.status === 'fulfilled' && result.value.caseId === caseData.id
            );
            
            if (statusResult && statusResult.status === 'fulfilled') {
              console.log('Updating case', caseData.caseNumber, 'with refund status:', statusResult.value.refundStatus);
              return {
                ...caseData,
                refund_status: statusResult.value.refundStatus
              };
            }
            return caseData;
          });
          
         console.log('Updated cases:', updatedCases.length);
         casesRef.current = updatedCases;
         return updatedCases;
        });
      } catch (error) {
        console.error('Error fetching refund statuses:', error);
      } finally {
        isFetchingRefundStatuses.current = false;
      }
    };

   const handleFormSubmit = async (formData: {
    title: string; 
    description: string; 
    caseType: 'Question' | 'Refund'; 
    orderId?: string; 
    deliveryDate?: string; 
    productIds?: string[]; 
    refundReason?: string; 
  }) => {
    try {
      setError(null);
      
       if (editingCase) {
          // Edit existing case - call backend API
          try {
            await supportApi.updateCase(editingCase.caseNumber, {
              subject: formData.title,
              description: formData.description,
              case_type: formData.caseType.toLowerCase(),
              user_role: currentUser.role,
              user_id: currentUser.id
            });
            
            // Update local state after successful API call
            const updatedCases: SupportCase[] = cases.map(c => 
              c.id === editingCase.id 
                ? { ...c, title: formData.title, description: formData.description, caseType: formData.caseType }
                : c
            );
            setCases(updatedCases);
            casesRef.current = updatedCases;
            // Save to localStorage for persistence
            localStorage.setItem(`support-cases-${currentUser.id}`, JSON.stringify(updatedCases));
          } catch (error) {
            setError(error instanceof ApiError ? error.message : 'Failed to update support case');
            return; // Don't close modal if there's an error
          }
          setEditingCase(null);
         } else {
          // Create new case
          const newCaseData = await supportApi.createSupportCase({
             customer_id: currentUser.id,
            case_type: formData.caseType.toLowerCase(),
            subject: formData.title,
            description: formData.description,
            refund_request_id: undefined,
            evidence_files: [],
            order_id: formData.orderId || (formData.caseType === 'Refund' ? `ORD-${Date.now()}` : undefined),
            product_ids: formData.productIds || (formData.caseType === 'Refund' ? ['PROD-DEFAULT'] : undefined),
            delivery_date: formData.deliveryDate || (formData.caseType === 'Refund' ? new Date().toISOString().split('T')[0] : undefined)
          });
          
          // If case type is Refund, create a refund request automatically
          if (formData.caseType === 'Refund') {
            try {
               // Add delay to ensure support case is persisted
               console.log('Adding delay before creating refund request...');
               await new Promise(resolve => setTimeout(resolve, 1000));
               
               // Create refund request linked to this support case
              const refundResponse = await refundApi.createRefundRequest({
                case_number: newCaseData.case_number,
                customer_id: currentUser.id,
                order_id: formData.orderId || `ORD-${Date.now()}`,
                product_ids: formData.productIds || [],
                request_reason: formData.refundReason || formData.description || 'Refund request',
                evidence_photos: []
              });
             
              // Add small delay to ensure support case is available
              await new Promise(resolve => setTimeout(resolve, 500));
              
              // Update support case to link the refund request
               await supportApi.updateCaseType(newCaseData.case_number, { 
                 case_type: 'refund', 
                 refund_request_id: refundResponse.refund_case_id 
               });
             
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
               casesRef.current = [newCase, ...cases];
               // Save to localStorage for persistence
               localStorage.setItem(`support-cases-${currentUser.id}`, JSON.stringify([newCase, ...cases]));
            } catch (err: any) {
              // If refund creation fails, still create the support case but show error
              console.error('Failed to create refund request:', err);
              
              // Check if the error is about support case not found (timing issue)
              const isSupportCaseNotFound = err?.message?.includes('Support case') && err?.message?.includes('not found');
              
              console.log('Refund creation failed details:', {
                error: err,
                errorMessage: err?.message,
                caseNumber: newCaseData.case_number,
                orderId: formData.orderId,
                productIds: formData.productIds,
                refundReason: formData.refundReason,
                isSupportCaseNotFound
              });
              
              let status: 'Open' | 'In Progress' | 'Closed';
              switch(newCaseData.status) {
                case 'closed': status = 'Closed'; break;
                case 'in_progress': status = 'In Progress'; break;
                default: status = 'Open';
              }
              
             let caseType: 'Question' | 'Refund';
             // Handle case type mapping with better error handling
             if (newCaseData.case_type === 'refund' || newCaseData.case_type === 'Refund') {
               caseType = 'Refund';
             } else {
               caseType = 'Question';
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
               casesRef.current = [newCase, ...cases];
               
               const errorMessage = isSupportCaseNotFound
                ? 'Support case created successfully, but refund service encountered timing issue. Please try creating refund request again later.'
                : '';
              
              setError(errorMessage);
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
            casesRef.current = [newCase, ...cases];
            // Save to localStorage for persistence
             localStorage.setItem(`support-cases-${currentUser.id}`, JSON.stringify([newCase, ...cases]));
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
      casesRef.current = updatedCases;
      
      // Refresh the cases list to get updated status (to sync with backend)
      fetchSupportCases();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to close support case');
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
           <div className="flex justify-between items-start">
             <div>
               <h1 className="text-4xl font-bold text-gray-800 mb-2">
                 📋 Support Case Dashboard
               </h1>
               <p className="text-gray-600 text-lg">
                 Manage your support cases and create refund requests
                </p>
                <div className="mt-2 text-sm text-blue-600">
                  Cases with refunds: {cases.filter(c => c.refund_request_id).length} | Questions: {cases.filter(c => c.caseType === 'Question').length}
                </div>
              </div>
             <div className="flex items-center space-x-4">
               <div className="bg-blue-50 px-4 py-2 rounded-lg">
                 <span className="text-blue-700 font-medium">{currentUser.name}</span>
                 <span className="bg-blue-200 text-blue-800 px-2 py-1 rounded-full text-xs font-semibold uppercase ml-2">
                   {currentUser.role}
                 </span>
               </div>
               <button 
                 onClick={() => {
                   const newRole = currentUser.role === 'customer' ? 'agent' : 'customer';
                    const newUser = {
                      ...currentUser,
                      role: newRole as 'customer' | 'agent' | 'admin',
                      id: newRole === 'customer' ? 'cust-123' : 'agent-001',
                      name: newRole === 'customer' ? 'Demo Customer' : 'Demo Agent'
                    };
                  setCurrentUser(newUser);
                    // Update URL with new role
                    window.history.replaceState(null, '', `/support-cases?role=${newRole}`);
                    fetchSupportCases();
                 }}
                 className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
               >
                 Switch to {currentUser.role === 'customer' ? 'Agent' : 'Customer'}
               </button>
             </div>
           </div>
         </div>

         <SupportCaseForm
           isOpen={showModal}
           onClose={handleModalClose}
           onSubmit={handleFormSubmit}
           editingCase={editingCase}
           currentUser={currentUser}
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
                  {currentUser.role === 'customer' ? 'My Support Cases' : 'All Support Cases'}
                </h2>
               {currentUser.role === 'customer' ? (
                 <button
                   onClick={startCreatingCase}
                   disabled={loading}
                   className="btn-primary px-6 py-3 text-lg flex items-center disabled:opacity-50"
                 >
                   <span className="mr-2">➕</span>
                   {loading ? 'Loading...' : 'Create New Case'}
                 </button>
               ) : (
                 <div className="text-sm text-gray-600 bg-blue-50 px-4 py-2 rounded-lg">
                   🛠️ Agents manage existing cases but cannot create new ones
                 </div>
               )}
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
                      {supportCase.caseType === 'Refund' && (
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          !supportCase.refund_status || supportCase.refund_status === 'unknown' ? 'bg-gray-100 text-gray-800' :
                          supportCase.refund_status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                          supportCase.refund_status === 'approved' ? 'bg-green-100 text-green-800' :
                          supportCase.refund_status === 'rejected' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                           {!supportCase.refund_status || supportCase.refund_status === 'unknown' ? '⏳ Checking...' :
                           supportCase.refund_status === 'pending' ? '⏳ Pending' :
                           supportCase.refund_status === 'approved' ? '✅ Approved' :
                           supportCase.refund_status === 'rejected' ? '❌ Rejected' :
                           '❓ ' + supportCase.refund_status}
                        </span>
                      )}
                    </div>
                     <div className="grid grid-cols-1 gap-2 text-xs text-gray-500 mb-4">
                       <div><span className="font-medium">Created:</span> {supportCase.created}</div>
                       <div><span className="font-medium">Last updated:</span> {supportCase.updated}</div>
                     </div>
                       <div className="action-buttons">
                          <Link 
                            to={`/support-cases/${supportCase.caseNumber}?role=${currentUser.role}`}
                            className="btn-primary"
                          >
                            📋 View Details
                          </Link>
                           {supportCase.status !== 'Closed' && currentUser.role === 'customer' && (
                            <button
                              onClick={() => startEditingCase(supportCase)}
                              className="btn-secondary"
                            >
                              ✏️ Edit
                            </button>
                           )}

                        {!supportCase.refund_request_id && supportCase.caseType === 'Refund' && supportCase.status !== 'Closed' && (
                          <span className="refund-status-message text-xs">
                            Case already configured for refund
                          </span>
                        )}
                          {supportCase.status !== 'Closed' && (
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