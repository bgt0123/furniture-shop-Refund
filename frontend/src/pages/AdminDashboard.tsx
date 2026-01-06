import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { AdminRefundList } from '../../components/AdminRefundList'
import { AdminRefundDetail } from '../../components/AdminRefundDetail'
import { adminApi } from '../../services/adminApi'
import { Layout } from '../../components/Layout'
import { Button } from '../../components/Button'
import { RefundCase } from '../../types/refundTypes'
import './AdminDashboard.css'

export const AdminDashboard: React.FC = () => {
  const [refundCases, setRefundCases] = useState<RefundCase[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedCase, setSelectedCase] = useState<RefundCase | null>(null)
  const [filterStatus, setFilterStatus] = useState<string | null>(null)
  const [searchCustomerId, setSearchCustomerId] = useState('')
  const navigate = useNavigate()

  // Get token from localStorage or sessionStorage
  const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken')

  useEffect(() => {
    if (!token) {
      navigate('/login')
      return
    }

    const fetchRefundCases = async () => {
      try {
        setLoading(true)
        setError(null)

        // Prepare query parameters
        const params: any = {}
        if (filterStatus) {
          params.status = filterStatus
        }
        if (searchCustomerId.trim()) {
          params.customerId = searchCustomerId.trim()
        }

        const response = await adminApi.getAllRefundCases(token, params)
        setRefundCases(response.data)
      } catch (err) {
        console.error('Error fetching refund cases:', err)
        setError('Failed to load refund cases. Please try again.')
      } finally {
        setLoading(false)
      }
    }

    fetchRefundCases()
  }, [token, filterStatus, searchCustomerId, navigate])

  const handleViewDetails = async (refundId: string) => {
    try {
      const response = await adminApi.getRefundCaseDetails(token, refundId)
      setSelectedCase(response.data)
    } catch (err) {
      console.error('Error fetching refund case details:', err)
      setError('Failed to load refund case details.')
    }
  }

  const handleApprove = async (refundId: string) => {
    try {
      await adminApi.approveRefund(token, refundId)
      // Refresh the list
      const response = await adminApi.getAllRefundCases(token)
      setRefundCases(response.data)
      setSelectedCase(null) // Close detail view
    } catch (err) {
      console.error('Error approving refund:', err)
      setError('Failed to approve refund.')
    }
  }

  const handleReject = async (refundId: string, reason: string) => {
    try {
      await adminApi.rejectRefund(token, refundId, reason)
      // Refresh the list
      const response = await adminApi.getAllRefundCases(token)
      setRefundCases(response.data)
      setSelectedCase(null) // Close detail view
    } catch (err) {
      console.error('Error rejecting refund:', err)
      setError('Failed to reject refund.')
    }
  }

  const handleComplete = async (refundId: string) => {
    try {
      // For demo purposes, we'll just refresh the list
      // In a real implementation, this would call a complete endpoint
      const response = await adminApi.getAllRefundCases(token)
      setRefundCases(response.data)
      setSelectedCase(null) // Close detail view
    } catch (err) {
      console.error('Error completing refund:', err)
      setError('Failed to complete refund.')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('authToken')
    sessionStorage.removeItem('authToken')
    navigate('/login')
  }

  if (!token) {
    return null // Redirect handled by useEffect
  }

  return (
    <Layout>
      <div className="admin-dashboard">
        <div className="dashboard-header">
          <h1>Support Agent Dashboard</h1>
          <div className="header-actions">
            <Button variant="secondary" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </div>

        <div className="dashboard-filters">
          <div className="filter-group">
            <label htmlFor="status-filter">Status:</label>
            <select
              id="status-filter"
              value={filterStatus || ''}
              onChange={(e) => setFilterStatus(e.target.value || null)}
            >
              <option value="">All Statuses</option>
              <option value="Pending">Pending</option>
              <option value="Approved">Approved</option>
              <option value="Rejected">Rejected</option>
              <option value="Completed">Completed</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="customer-search">Customer ID:</label>
            <input
              id="customer-search"
              type="text"
              value={searchCustomerId}
              onChange={(e) => setSearchCustomerId(e.target.value)}
              placeholder="Search by customer ID"
            />
          </div>

          <Button 
            variant="primary" 
            onClick={() => {
              setFilterStatus(null)
              setSearchCustomerId('')
            }}
          >
            Reset Filters
          </Button>
        </div>

        {error && (
          <div className="error-message">
            <p>{error}</p>
            <Button variant="secondary" onClick={() => setError(null)}>
              Dismiss
            </Button>
          </div>
        )}

        <div className="dashboard-content">
          {loading ? (
            <div className="loading-spinner">
              <p>Loading refund cases...</p>
            </div>
          ) : selectedCase ? (
            <AdminRefundDetail
              refundCase={selectedCase}
              onClose={() => setSelectedCase(null)}
              onApprove={() => handleApprove(selectedCase.id)}
              onReject={(reason) => handleReject(selectedCase.id, reason)}
              onComplete={() => handleComplete(selectedCase.id)}
              token={token}
            />
          ) : (
            <AdminRefundList
              cases={refundCases}
              onViewDetails={handleViewDetails}
              onApprove={handleApprove}
              onReject={handleReject}
              token={token}
            />
          )}
        </div>

        <div className="dashboard-stats">
          <div className="stat-card">
            <h3>Total Cases</h3>
            <p>{refundCases.length}</p>
          </div>
          <div className="stat-card">
            <h3>Pending</h3>
            <p>{refundCases.filter(c => c.status === 'Pending').length}</p>
          </div>
          <div className="stat-card">
            <h3>Approved</h3>
            <p>{refundCases.filter(c => c.status === 'Approved').length}</p>
          </div>
          <div className="stat-card">
            <h3>Completed</h3>
            <p>{refundCases.filter(c => c.status === 'Completed').length}</p>
          </div>
        </div>
      </div>
    </Layout>
  )
}