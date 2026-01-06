import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { supportApi } from '../../services/supportApi'
import { SupportCase } from '../../types/supportTypes'
import { Button } from '../Button'

interface SupportCaseListProps {
  cases: SupportCase[]
  onViewDetails: (caseId: string) => void
  token: string
}

export const SupportCaseList: React.FC<SupportCaseListProps> = ({ cases, onViewDetails, token }) => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleCloseCase = async (caseId: string) => {
    try {
      setIsLoading(true)
      setError(null)
      
      supportApi.setAuthToken(token)
      await supportApi.closeSupportCase(caseId)
      
      // Refresh the list (this would typically be handled by parent component)
      window.location.reload()
    } catch (err) {
      console.error('Error closing case:', err)
      setError('Failed to close case. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  if (cases.length === 0) {
    return (
      <div className="support-case-list empty">
        <p>No support cases found.</p>
        <Link to="/support/create">
          <Button variant="primary">Create New Support Case</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="support-case-list">
      <h2>Your Support Cases</h2>
      {error && <div className="error-message">{error}</div>}
      
      <div className="case-grid">
        {cases.map((supportCase) => (
          <div key={supportCase.id} className="case-card">
            <div className="case-header">
              <span className={`status-badge ${supportCase.status.toLowerCase()}`}>
                {supportCase.status}
              </span>
              <span className="case-id">Case #{supportCase.id.substring(0, 8)}</span>
            </div>
            
            <div className="case-body">
              <p className="issue-description">{supportCase.issueDescription}</p>
              <p className="order-info">Order: {supportCase.orderId}</p>
              <p className="created-at">Created: {new Date(supportCase.createdAt).toLocaleString()}</p>
              <p className="products-count">Products: {supportCase.products?.length || 0}</p>
            </div>
            
            <div className="case-actions">
              <Button 
                variant="secondary" 
                onClick={() => onViewDetails(supportCase.id)}
                size="small"
              >
                View Details
              </Button>
              
              {supportCase.status === 'Open' && (
                <Button
                  variant="primary"
                  onClick={() => handleCloseCase(supportCase.id)}
                  size="small"
                  disabled={isLoading}
                >
                  {isLoading ? 'Closing...' : 'Close Case'}
                </Button>
              )}
            </div>
          </div>
        ))}
      </div>
      
      <div className="list-actions">
        <Link to="/support/create">
          <Button variant="primary">Create New Support Case</Button>
        </Link>
      </div>
    </div>
  )
}