import React from 'react'

interface SupportCase {
  case_id: string
  customer_id: string
  order_id: string
  title: string
  description: string
  status: 'open' | 'in_progress' | 'resolved' | 'closed'
  created_at: string
  updated_at: string
}

interface SupportCaseListProps {
  cases: SupportCase[]
  onSelectCase?: (caseId: string) => void
}

const SupportCaseList: React.FC<SupportCaseListProps> = ({ cases, onSelectCase }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'status-open'
      case 'in_progress': return 'status-in-progress'
      case 'resolved': return 'status-resolved'
      case 'closed': return 'status-closed'
      default: return 'status-default'
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <div className="support-case-list">
      {cases.length === 0 ? (
        <div className="empty-state">
          <p>No support cases found</p>
        </div>
      ) : (
        <div className="cases-grid">
          {cases.map((caseItem) => (
            <div
              key={caseItem.case_id}
              className={`support-case-card ${onSelectCase ? 'clickable' : ''}`}
              onClick={() => onSelectCase && onSelectCase(caseItem.case_id)}
            >
              <div className="case-header">
                <h3 className="case-title">{caseItem.title}</h3>
                <span className={`status-badge ${getStatusColor(caseItem.status)}`}>
                  {caseItem.status.replace('_', ' ')}
                </span>
              </div>
              
              <p className="case-description">{caseItem.description}</p>
              
              <div className="case-details">
                <span className="detail-item">
                  Order #: {caseItem.order_id}
                </span>
                <span className="detail-item">
                  Created: {formatDate(caseItem.created_at)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SupportCaseList