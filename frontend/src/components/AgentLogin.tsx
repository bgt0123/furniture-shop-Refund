import React, { useState } from 'react';
import { Card, Button, LoadingSpinner } from '../components';
import { agentApiService } from '../services/agentApi';

const AgentLogin: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await agentApiService.loginAgent(email, password);
      
      // Set authentication tokens
      const token = response.data.access_token;
      const agentId = response.data.agent_id;
      agentApiService.setAgentAuth(token, agentId);
      
      // Redirect to dashboard
      window.location.href = '/agent-dashboard';
      
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  // If already authenticated, redirect to dashboard
  if (agentApiService.isAgentAuthenticated()) {
    window.location.href = '/agent-dashboard';
    return null;
  }

  return (
    <div className="agent-login">
      <Card>
        <div className="login-container">
          <h2>Agent Login</h2>
          <p>Sign in to access the support agent dashboard</p>
          
          <form onSubmit={handleSubmit} className="login-form">
            {error && <div className="error-message">{error}</div>}
            
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="agent@furnitureshop.com"
                className="form-input"
                disabled={loading}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="form-input"
                disabled={loading}
              />
            </div>
            
            <Button 
              type="submit" 
              variant="primary" 
              disabled={loading}
            >
              {loading ? (
                <><LoadingSpinner size="sm" /> Signing in...</>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>
          
          <div className="login-footer">
            <p>
              <a href="/">← Back to Customer Portal</a>
            </p>
          </div>
        </div>

        <style>{`
          .agent-login {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #f5f5f5;
            padding: 20px;
          }
          
          .login-container {
            max-width: 400px;
            width: 100%;
            text-align: center;
          }
          
          .login-container h2 {
            margin-bottom: 10px;
            color: #333;
          }
          
          .login-container p {
            margin-bottom: 30px;
            color: #666;
          }
          
          .login-form {
            text-align: left;
          }
          
          .form-group {
            margin-bottom: 20px;
          }
          
          .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
          }
          
          .form-input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
            box-sizing: border-box;
          }
          
          .form-input:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
          }
          
          .form-input:disabled {
            background-color: #f8f9fa;
            opacity: 0.7;
          }
          
          .login-button {
            width: 100%;
            margin-top: 10px;
          }
          
          .error-message {
            background-color: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 20px;
            text-align: center;
          }
          
          .login-footer {
            margin-top: 30px;
            text-align: center;
          }
          
          .login-footer a {
            color: #007bff;
            text-decoration: none;
          }
          
          .login-footer a:hover {
            text-decoration: underline;
          }
        `}</style>
      </Card>
    </div>
  );
};

export default AgentLogin;