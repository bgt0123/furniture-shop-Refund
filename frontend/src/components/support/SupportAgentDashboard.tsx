import React, { useState, useEffect } from 'react'
import { refundCaseService } from '../../services/refundCaseService'

interface RefundCase {
  refund_id: string
  support_case_id: string
  status: 'pending' | 'approved' | 'executed' | 'failed' | 'cancelled'
  requested_amount: number
  approved_amount?: number
  delivery_date: string
  refund_requested_at: string
  refund_approved_at?: string
}

const SupportAgentDashboard: React.FC = () => {
  const [pendingRefunds, setPendingRefunds] = useState<RefundCase[]>([])
  // const [selectedCase, setSelectedCase] = useState<RefundCase | null>(null)

  useEffect(() => {
    loadPendingRefunds()
  }, [])

  const loadPendingRefunds = async () => {
    try {
      const refunds = await refundCaseService.getPendingRefunds()
      setPendingRefunds(refunds)
    } catch (error) {
      console.error('Failed to load pending refunds:', error)
    }
  }

  const approveRefund = async (refundId: string, amount?: number) => {
    try {
      await refundCaseService.approveRefund(refundId, amount)
      await loadPendingRefunds()
      alert('Refund approved successfully')
    } catch (error) {
      console.error('Failed to approve refund:', error)
      alert('Failed to approve refund')
    }
  }

  const executeRefund = async (refundId: string) => {
    try {
      await refundCaseService.executeRefund(refundId)
      await loadPendingRefunds()
      alert('Refund executed successfully')
    } catch (error) {
      console.error('Failed to execute refund:', error)
      alert('Failed to execute refund')
    }
  }

  return (
    <div className="agent-dashboard">
      <h2>Support Agent Dashboard</h2>
      <p>Manage refund requests and approvals</p>
      
      <div className="dashboard-sections">
        <div className="pending-refunds-section">
          <h3>Pending Refund Requests</h3>
          {pendingRefunds.length === 0 ? (
            <p>No pending refund requests</p>
          ) : (
            <table className="refunds-table">
              <thead>
                <tr>
                  <th>Refund ID</th>
                  <th>Support Case</th>
                  <th>Amount</th>
                  <th>Delivery Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {pendingRefunds.map((refund) => (
                  <tr key={refund.refund_id}>
                    <td>{refund.refund_id.slice(0, 8)}...</td>
                    <td>{refund.support_case_id.slice(0, 8)}...</td>
                    <td>${refund.requested_amount.toFixed(2)}</td>
                    <td>{new Date(refund.delivery_date).toLocaleDateString()}</td>
                    <td>
                      <button 
                        className="approve-button"
                        onClick={() => approveRefund(refund.refund_id)}
                      >
                        Approve
                      </button>
                      <button 
                        className="execute-button"
                        onClick={() => executeRefund(refund.refund_id)}
                      >
                        Execute
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}

export default SupportAgentDashboard