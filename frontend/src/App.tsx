import { useState } from 'react'
import SupportCaseForm from './components/support/SupportCaseForm'
import SupportCaseList from './components/support/SupportCaseList'
import SupportAgentDashboard from './components/support/SupportAgentDashboard'
import { supportCaseService } from './services/supportCaseService'
import './App.css'

type SupportCase = {
  case_id: string
  customer_id: string
  order_id: string
  title: string
  description: string
  status: 'open' | 'in_progress' | 'resolved' | 'closed'
  created_at: string
  updated_at: string
}

function App() {
  const [supportCases, setSupportCases] = useState<SupportCase[]>([])
  const [showForm, setShowForm] = useState(false)
  const [showAgentDashboard, setShowAgentDashboard] = useState(false)

  const handleCreateSupportCase = async (formData: any) => {
    try {
      const newCase = await supportCaseService.createSupportCase(formData)
      setSupportCases(prev => [...prev, newCase])
      setShowForm(false)
    } catch (error) {
      console.error('Failed to create support case:', error)
      alert('Failed to create support case. Please try again.')
    }
  }

  const loadSupportCases = async () => {
    try {
      const cases = await supportCaseService.getMySupportCases()
      setSupportCases(cases)
    } catch (error) {
      console.error('Failed to load support cases:', error)
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Furniture Shop Refund System</h1>
      </header>
      <main>
        <div className="container">
          <h2>Customer Support and Refund Management</h2>
          <p>Welcome to the Furniture Shop Customer Support System</p>
          
          <div className="support-section">
      <div className="actions-bar">
        <button 
          className="primary-button"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : 'Create Support Case'}
        </button>
        <button 
          className="secondary-button"
          onClick={loadSupportCases}
        >
          View My Cases
        </button>
        <button 
          className="agent-button"
          onClick={() => setShowAgentDashboard(!showAgentDashboard)}
        >
          Support Agent Dashboard
        </button>
      </div>

            {showAgentDashboard ? (
              <div className="agent-dashboard-section">
                <h3>Support Agent Dashboard</h3>
                <SupportAgentDashboard />
              </div>
            ) : (
              <>
                {showForm && (
                  <div className="form-section">
                    <h3>Create New Support Case</h3>
                    <SupportCaseForm onSubmit={handleCreateSupportCase} />
                  </div>
                )}

                <div className="list-section">
                  <h3>My Support Cases</h3>
                  <SupportCaseList 
                    cases={supportCases} 
                    onSelectCase={(caseId: string) => console.log('Selected case:', caseId)}
                  />
                </div>
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
