import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { refundApi } from '../../services/api';

interface RefundCase {
  refund_case_id: string;
  case_number: string;
  customer_id: string;
  order_id: string;
  status: string;
  created_at: string;
  updated_at: string;
}

interface RefundRequest {
  refund_request_id?: string;
  product_ids: string[];
  request_reason: string;
  evidence_photos?: string[];
}

interface RefundCaseWithDetails extends RefundCase {
  refund_request?: RefundRequest;
  supportCaseTitle?: string;
  supportCaseDescription?: string;
}

const RefundCaseDashboard: React.FC = () => {
  const [refundCases, setRefundCases] = useState<RefundCaseWithDetails[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // const mockCustomerId = 'cust-123'; // Unused for now

  useEffect(() => {
    // Only fetch cases if we're on the dashboard (not on a detail page)
    if (window.location.pathname === '/refund-cases') {
      fetchRefundCases();
    }
  }, []);

  const fetchRefundCases = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const mockCustomerId = 'cust-123'; // Mock customer ID for now
      console.log('Fetching refund cases for customer:', mockCustomerId);
      
      // Fetch refund cases from the backend API
      const fetchedCases = await refundApi.getCustomerRefundCases(mockCustomerId);
      console.log('Fetched refund cases:', fetchedCases);
      
      const casesWithDetails: RefundCaseWithDetails[] = fetchedCases.map(caseData => ({
        ...caseData,
        supportCaseTitle: `Support case #${caseData.case_number}`,
        supportCaseDescription: `Refund request for order ${caseData.order_id}`
      }));
      
      setRefundCases(casesWithDetails);
      
      if (fetchedCases.length === 0) {
        setError('No refund cases found. Create a refund request first.');
      }
    } catch (err: any) {
      // Handle specific API errors
      if (err.statusCode === 404 || err.message.includes('not available') || err.message.includes('Failed to fetch')) {
        setError('Refund service endpoint not available. Make sure refund service is running.');
      } else {
        const errorMessage = err.message || 'Failed to load refund cases';
        setError(errorMessage);
      }
      setRefundCases([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusDisplay = (status: string) => {
    const statusMap = {
      'pending': { emoji: '⏳', text: 'Pending Review', className: 'bg-yellow-100 text-yellow-900' },
      'approved': { emoji: '✅', text: 'Approved', className: 'bg-green-100 text-green-800' },
      'rejected': { emoji: '❌', text: 'Rejected', className: 'bg-red-100 text-red-800' },
      'processing': { emoji: '🔄', text: 'Processing', className: 'bg-blue-100 text-blue-800' }
    };
    
    return statusMap[status as keyof typeof statusMap] || 
           { emoji: '❓', text: status, className: 'bg-gray-100 text-gray-800' };
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'Unknown date';
    }
  };

  return (
    <div className="refund-case-dashboard min-h-screen bg-gradient-to-br from-green-100 to-emerald-200 p-6 app">
      <div className="max-w-6xl mx-auto support-dashboard">
        <div className="header-section mb-8">
          <h1 className="text-4xl font-bold mb-2">
            💸 Refund Case Dashboard
          </h1>
          <p className="text-lg">
            Track and manage refund cases and their status
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-3">
            <div className="bg-green-50 border border-green-200 rounded-xl shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-semibold">
                  My Refund Cases
                </h2>
                <span className="text-sm bg-green-500 text-white px-3 py-1 rounded-full font-medium whitespace-nowrap">
                  {refundCases.length} Cases
                </span>
              </div>

              {loading ? (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
                  <p className="mt-2 text-gray-600">Loading refund cases...</p>
                </div>
              ) : refundCases.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-600">No refund cases found.</p>
                </div>
                 ) : (
                   <div className="case-list space-y-4">
                   {refundCases.map((caseData) => {
                     const statusInfo = getStatusDisplay(caseData.status);
                     const borderColorMap = {
                       'pending': 'border-yellow-500',
                       'approved': 'border-green-500',
                       'rejected': 'border-red-500',
                       'processing': 'border-blue-500'
                     };
                     const borderColor = borderColorMap[caseData.status as keyof typeof borderColorMap] || 'border-gray-500';
                     
                     return (
                       <div key={caseData.refund_case_id} className={`case-item bg-gradient-to-r from-white to-green-50 border-l-4 ${borderColor} p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-300 case-card`}>
                        <div className="flex justify-between items-center mb-2 gap-4">
                          <span className="case-number font-mono text-sm text-gray-600 flex-1">
                            Case #{caseData.refund_case_id}
                          </span>
                          <span className={`status status-pending px-3 py-1 ${statusInfo.className} rounded-full text-sm font-medium flex-shrink-0`}>
                            {statusInfo.emoji} {statusInfo.text}
                          </span>
                        </div>
                         <h3 className="text-lg font-medium mb-1">
                           Refund Request #{caseData.refund_case_id}
                         </h3>
                         <p className="text-gray-600 text-sm mb-2">
                           {caseData.order_id ? `Refund request for order ${caseData.order_id}` : 'Refund request'}
                         </p>
                        <div className="grid grid-cols-2 gap-4 text-xs text-gray-500 mb-3">
                          <div>Support Case: #{caseData.case_number}</div>
                          <div className="text-right">Created: {formatDate(caseData.created_at)}</div>
                        </div>
                         <div className="flex space-x-2">
                           <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                             Refund Case
                           </span>
                           {caseData.case_number && (
                             <Link
                               to={`/support-cases/${caseData.case_number}`}
                               className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs hover:bg-green-200 no-underline"
                             >
                               Support Case #{caseData.case_number}
                             </Link>
                           )}
                         </div>
                          <div className="action-buttons">
                            <Link 
                              to={`/refund-cases/${caseData.refund_case_id}`}
                              className="btn-primary"
                            >
                              📋 View Details
                            </Link>
                          </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RefundCaseDashboard;