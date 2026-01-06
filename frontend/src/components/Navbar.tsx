import React from 'react'
import { Link } from 'react-router-dom'

interface NavbarProps {
  user?: {
    username: string
    roles: string[]
  }
  onLogout: () => void
}

export const Navbar: React.FC<NavbarProps> = ({ user, onLogout }) => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">Furniture Shop Support</Link>
      </div>
      <div className="navbar-links">
        <Link to="/support">Support Cases</Link>
        <Link to="/refunds">Refund Cases</Link>
        {user?.roles.includes('admin') && (
          <Link to="/admin">Admin Dashboard</Link>
        )}
      </div>
      <div className="navbar-auth">
        {user ? (
          <>
            <span>Welcome, {user.username}</span>
            <button onClick={onLogout}>Logout</button>
          </>
        ) : (
          <Link to="/login">Login</Link>
        )}
      </div>
    </nav>
  )
}