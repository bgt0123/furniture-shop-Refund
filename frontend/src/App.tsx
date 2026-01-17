import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import SupportDashboard from './pages/SupportDashboard'
import RefundDashboard from './pages/RefundDashboard'
import AgentPortal from './pages/AgentPortal'
import AgentLogin from './components/AgentLogin'
import './App.css'
import './styles/refund.css'

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          {/* Customer routes */}
          <Route path="/" element={<SupportDashboard />} />
          <Route path="/support" element={<SupportDashboard />} />
          <Route path="/refunds" element={<RefundDashboard />} />
          
          {/* Agent routes */}
          <Route path="/agent-login" element={<AgentLogin />} />
          <Route path="/agent-dashboard" element={<AgentPortal />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
