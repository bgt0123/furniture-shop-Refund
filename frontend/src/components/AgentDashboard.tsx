import React, { useState, useEffect } from 'react';
import { Card, Button, LoadingSpinner } from '../components';
import { agentApiService } from '../services/agentApi';
import { RefundCaseAdminList } from '../types/models';
import AgentRefundList from './AgentRefundList';
import RefundProcessingForm from './RefundProcessingForm';

const AgentDashboard: React.FC = () => {
  const [refundCases, setRefundCases] = useState<RefundCaseAdminList[]>([]);
  const [selectedCase, setSelectedCase] = useState<RefundCaseAdminList | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'pending' | 'all'>('pending');

  useEffect(() => {
    loadRefundCases();
  }, [activeTab]);

  const loadRefundCases = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let response;
      if (activeTab === 'pending') {
        response = await agentApiService.getPendingRefundCases();
      } else {
        response = await agentApiService.getAdminRefundCases();
      }
      
      setRefundCases(response.data);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load refund cases');
    } finally {
      setLoading(false);
    }
  };

  const handleCaseSelect = (caseItem: RefundCaseAdminList) => {
    setSelectedCase(caseItem);
  };

  const handleCaseProcessed = () => {
    setSelectedCase(null);
    loadRefundCases();
  };

  const handleLogout = () => {
    agentApiService.clearAgentAuth();
    window.location.href = '/agent-login';
  };

  if (!agentApiService.isAgentAuthenticated()) {
    window.location.href = '/agent-login';
    return null;
  }

  return (
    <div className="agent-dashboard">
      <div className="dashboard-header">
        <h1>Support Agent Dashboard</h1>
        <div className="agent-actions">
          <Button onClick={handleLogout} variant="secondary">Logout</Button>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="cases-section">
          <Card>
            <div className="tab-navigation">
              <button 
                className={`tab-button ${activeTab === 'pending' ? 'active' : ''}`}
                onClick={() => setActiveTab('pending')}
              >
                Pending Cases ({refundCases.filter(c => c.status === 'Pending').length})
              </button>
              <button 
                className={`tab-button ${activeTab === 'all' ? 'active' : ''}`}
                onClick={() => setActiveTab('all')}
              >
                All Cases ({refundCases.length})
              </button>
            </div>

            {loading && <div className="loading-container"><LoadingSpinner /> Loading cases...</div>}
            
            {error && <div className="error-message">{error}</div>}

            {!loading && !error && (
              <AgentRefundList 
                cases={refundCases}
                onCaseSelect={handleCaseSelect}
                selectedCaseId={selectedCase?.id}
              />
            )}
          </Card>
        </div>

        <div className="processing-section">
          {selectedCase ? (
            <RefundProcessingForm 
              refundCase={selectedCase}
              onProcessed={handleCaseProcessed}
              onCancel={() => setSelectedCase(null)}
            />
          ) : (
            <Card>
              <div className="no-case-selected">
                <h3>Select a refund case to process</h3>
                <p>Click on a refund case from the list to approve or reject it.</p>
              </div>
            </Card>
          )}
        </div>
      </div>

      <style>{`
        .agent-dashboard {
          padding: 20px;
          min-height: 100vh;
          background-color: #f5f5f5;
        }
        
        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }
        
        .dashboard-content {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
        }
        
        .tab-navigation {
          display: flex;
          margin-bottom: 20px;
          border-bottom: 1px solid #ddd;
        }
        
        .tab-button {
          padding: 10px 20px;
          background: none;
          border: none;
          border-bottom: 2px solid transparent;
          cursor: pointer;
          transition: all 0.3s;
        }
        
        .tab-button.active {
          border-bottom-color: #007bff;
          color: #007bff;
        }
        
        .tab-button:hover {
          background-color: #f8f9fa;
        }
        
        .loading-container {
          text-align: center;
          padding: 40px;
        }
        
        .error-message {
          background-color: #f8d7da;
          color: #721c24;
          padding: 10px;
          border-radius: 4px;
          margin-bottom: 20px;
        }
        
        .no-case-selected {
          text-align: center;
          padding: 40px;
          color: #6c757d;
        }
        
        @media (max-width: 768px) {
          .dashboard-content {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default AgentDashboard;