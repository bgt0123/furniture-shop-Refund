import React from 'react'
import { Link } from 'react-router-dom'

interface LayoutProps {
  children: React.ReactNode
  user?: {
    username: string
    roles: string[]
  }
  onLogout: () => void
}

export const Layout: React.FC<LayoutProps> = ({ children, user, onLogout }) => {
  return (
    <div className="app-layout">
      <header>
        <h1>Customer Support and Refund Service</h1>
      </header>
      <main className="app-content">
        {children}
      </main>
      <footer className="app-footer">
        <p>© {new Date().getFullYear()} Furniture Shop. All rights reserved.</p>
      </footer>
    </div>
  )
}