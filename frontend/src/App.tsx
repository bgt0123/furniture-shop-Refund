import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { CustomerDashboard } from './pages/customer/dashboard.tsx'
import { AgentDashboard } from './pages/agent/dashboard.tsx'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/customer/*" element={<CustomerDashboard />} />
          <Route path="/agent/*" element={<AgentDashboard />} />
          <Route path="/" element={<div>Welcome to Furniture Shop Support</div>} />
        </Routes>
      </div>
    </Router>
  )
}

export default App