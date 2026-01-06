import React from 'react'
import { Link } from 'react-router-dom'

interface LoginFormProps {
  onSubmit: (username: string, password: string) => void
  error?: string
  loading?: boolean
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSubmit, error, loading }) => {
  const [username, setUsername] = React.useState('')
  const [password, setPassword] = React.useState('')
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(username, password)
  }
  
  return (
    <div className="login-form">
      <h2>Login</h2>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      <div className="login-links">
        <Link to="/forgot-password">Forgot password?</Link>
      </div>
    </div>
  )
}