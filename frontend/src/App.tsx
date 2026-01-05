import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <Router>
      <div className="app">
        <header>
          <h1>Customer Support and Refund Service</h1>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<h2>Welcome to Support Service</h2>} />
            <Route path="/support" element={<h2>Support Cases</h2>} />
            <Route path="/refunds" element={<h2>Refund Cases</h2>} />
            <Route path="/admin" element={<h2>Admin Dashboard</h2>} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App