import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { SupportDashboard } from './pages/SupportDashboard'
import { RefundDashboard } from './pages/RefundDashboard'
import './App.css'
import './styles/refund.css'

function App() {
  return (
    <Router>
      <div className="app">
        <header>
          <h1>Customer Support and Refund Service</h1>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<SupportDashboard />} />
            <Route path="/support" element={<SupportDashboard />} />
            <Route path="/refunds" element={<RefundDashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
