import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Layout } from '../../components/Layout'
import { SupportCaseForm } from '../../components/SupportCaseForm'
import { SupportCaseList } from '../../components/SupportCaseList'
import { SupportCaseDetail } from '../../components/SupportCaseDetail'
import { supportApi } from '../../services/supportApi'
import { SupportCase } from '../../types/supportTypes'
import { Button } from '../../components/Button'

interface SupportDashboardProps {
  token: string
}

export const SupportDashboard: React.FC<SupportDashboardProps> = ({ token }) => {
  const [activeView, setActiveView] = useState<'list' | 'create' | 'detail'>('list')
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null)
  const [cases, setCases] = useState<SupportCase[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchCases = async () => {
      try {
        setIsLoading(true)
        setError(null)
        
        supportApi.setAuthToken(token)
        const response = await supportApi.getSupportCases()
        setCases(response.data.cases || [])
      } catch (err) {
        console.error('Error fetching support cases:', err)
        setError('Failed to load support cases. Please try again.')
      } finally {
        setIsLoading(false)
      }
    }
    
    if (token) {
      fetchCases()
    }
  }, [token])

  const handleCaseCreated = (newCase: SupportCase) => {
    setCases([...cases, newCase])
    setActiveView('list')
  }

  const handleViewDetails = (caseId: string) => {
    setSelectedCaseId(caseId)
    setActiveView('detail')
  }

  const handleBackToList = () => {
    setActiveView('list')
    setSelectedCaseId(null)
  }

  const renderContent = () => {
    switch (activeView) {
      case 'create':
        return (
          <SupportCaseForm 
            onCaseCreated={handleCaseCreated} 
            token={token}
          />
        )
      
      case 'detail':
        return (
          <SupportCaseDetail 
            token={token}
          />
        )
      
      case 'list':
      default:
        return (
          <SupportCaseList 
            cases={cases} 
            onViewDetails={handleViewDetails} 
            token={token}
          />
        )
    }
  }

  return (
    <Layout>
      <div className="support-dashboard">
        <div className="dashboard-header">
          <h1>Support Dashboard</h1>
          
          <div className="dashboard-actions">
            {activeView === 'list' && (
              <Button 
                variant="primary" 
                onClick={() => setActiveView('create')}
              >
                Create Support Case
              </Button>
            )}
            
            {activeView !== 'list' && (
              <Button 
                variant="secondary" 
                onClick={handleBackToList}
              >
                Back to List
              </Button>
            )}
          </div>
        </div>

        {error && (
          <div className="error-banner">
            <p>{error}</p>
            <Button variant="secondary" onClick={() => setError(null)}>
              Dismiss
            </Button>
          </div>
        )}

        <div className="dashboard-content">
          {isLoading && activeView === 'list' ? (
            <div className="loading">Loading support cases...</div>
          ) : (
            renderContent()
          )}
        </div>
      </div>
    </Layout>
  )
}