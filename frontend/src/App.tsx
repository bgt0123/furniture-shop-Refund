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
            <Route path="/" element={<div>Welcome to the Support and Refund Service</div>} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
