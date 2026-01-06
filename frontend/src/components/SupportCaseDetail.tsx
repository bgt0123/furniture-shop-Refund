import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { supportApi } from '../../services/supportApi'
import { SupportCase } from '../../types/supportTypes'
import { Button } from '../Button'

interface SupportCaseDetailProps {
  token: string
}

export const SupportCaseDetail: React.FC<SupportCaseDetailProps> = ({ token }) => {
  const { caseId } = useParams<{ caseId: string }>()
  const [supportCase, setSupportCase] = useState<SupportCase | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isClosing, setIsClosing] = useState(false)

  useEffect(() => {
    const fetchCaseDetails = async () => {
      try {
        setIsLoading(true)
        setError(null)
        
        supportApi.setAuthToken(token)
        const response = await supportApi.getSupportCase(caseId || '')
        setSupportCase(response.data)
      } catch (err) {
        console.error('Error fetching case details:', err)
        setError('Failed to load case details. Please try again.')
      } finally {
        setIsLoading(false)
      }
    }
    
    if (caseId) {
      fetchCaseDetails()
    }
  }, [caseId, token])

  const handleCloseCase = async () => {
    try {
      setIsClosing(true)
      setError(null)
      
      supportApi.setAuthToken(token)
      await supportApi.closeSupportCase(caseId || '')
      
      // Refresh case details
      const response = await supportApi.getSupportCase(caseId || '')
      setSupportCase(response.data)
    } catch (err) {
      console.error('Error closing case:', err)
      setError('Failed to close case. Please try again.')
    } finally {
      setIsClosing(false)
    }
  }

  const handleRequestRefund = () => {
    // Navigate to refund request page with case ID
    // This would be implemented in User Story 2
    console.log('Navigate to refund request for case:', caseId)
  }

  if (isLoading) {
    return <div className="loading">Loading case details...</div>
  }

  if (error) {
    return (
      <div className="error-container">
        <h3>Error</h3>
        <p>{error}</p>
        <Link to="/support">
          <Button variant="secondary">Back to Support Cases</Button>
        </Link>
      </div>
    )
  }

  if (!supportCase) {
    return (
      <div className="not-found">
        <h3>Support Case Not Found</h3>
        <p>The requested support case does not exist or you don't have permission to view it.</p>
        <Link to="/support">
          <Button variant="secondary">Back to Support Cases</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="support-case-detail">
      <div className="case-header">
        <div className="header-left">
          <h2>Support Case #{supportCase.id.substring(0, 8)}</h2>
          <span className={`status-badge ${supportCase.status.toLowerCase()}`}>
            {supportCase.status}
          </span>
        </div>
        
        <div className="header-right">
          <p>Created: {new Date(supportCase.createdAt).toLocaleString()}</p>
          {supportCase.closedAt && (
            <p>Closed: {new Date(supportCase.closedAt).toLocaleString()}</p>
          )}
        </div>
      </div>

      <div className="case-body">
        <div className="section">
          <h3>Issue Description</h3>
          <p>{supportCase.issueDescription}</p>
        </div>

        <div className="section">
          <h3>Order Information</h3>
          <p><strong>Order ID:</strong> {supportCase.orderId}</p>
        </div>

        <div className="section">
          <h3>Products</h3>
          <div className="products-list">
            {supportCase.products && supportCase.products.length > 0 ? (
              <ul>
                {supportCase.products.map((product, index) => (
                  <li key={index}>
                    <div className="product-info">
                      <span className="product-id">{product.productId}</span>
                      {product.name && <span className="product-name"> - {product.name}</span>}
                      <span className="product-quantity">Qty: {product.quantity}</span>
                      {product.price && <span className="product-price">${product.price.toFixed(2)}</span>}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No products specified</p>
            )}
          </div>
        </div>

        {supportCase.attachments && supportCase.attachments.length > 0 && (
          <div className="section">
            <h3>Attachments</h3>
            <div className="attachments-list">
              {supportCase.attachments.map((attachment, index) => (
                <div key={index} className="attachment-item">
                  <a href={attachment.url} target="_blank" rel="noopener noreferrer">
                    {attachment.name}
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="section">
          <h3>Case History</h3>
          <div className="history-list">
            {supportCase.history && supportCase.history.length > 0 ? (
              <ul>
                {supportCase.history.map((entry, index) => (
                  <li key={index} className="history-entry">
                    <div className="history-timestamp">
                      {new Date(entry.timestamp).toLocaleString()}
                    </div>
                    <div className="history-action">
                      {entry.action}
                    </div>
                    {entry.details && (
                      <div className="history-details">
                        {JSON.stringify(entry.details)}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            ) : (
              <p>No history entries</p>
            )}
          </div>
        </div>
      </div>

      <div className="case-actions">
        <Link to="/support">
          <Button variant="secondary">Back to List</Button>
        </Link>
        
        {supportCase.status === 'Open' && (
          <>
            <Button 
              variant="primary" 
              onClick={handleRequestRefund}
              disabled={isClosing}
            >
              Request Refund
            </Button>
            
            <Button
              variant="danger"
              onClick={handleCloseCase}
              disabled={isClosing}
            >
              {isClosing ? 'Closing...' : 'Close Case'}
            </Button>
          </>
        )}
      </div>
    </div>
  )
}