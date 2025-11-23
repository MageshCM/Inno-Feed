// src/components/Auth.jsx
import React, { useState } from 'react';
import './Auth.css';

function Auth({ onAuthSuccess, API_BASE_URL }) {
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    setIsLoading(true);

    const endpoint = isLogin ? 'login' : 'register';
    const body = isLogin ? { email, password } : { name, email, password };

    try {
      const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `HTTP error! status: ${response.status}`);
      }

      if (isLogin) {
        // On successful login, pass user_id and name from backend response
        onAuthSuccess(data.user_id, data.name || email.split('@')[0]);
      } else {
        setMessage('Registration successful! Please log in.');
        setIsLogin(true);
        setName('');
        setEmail('');
        setPassword('');
      }
    } catch (e) {
      setError(e.message);
      console.error('Auth error:', e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h2>{isLogin ? 'Log In' : 'Register'}</h2>
      {message && <p className="success-message">{message}</p>}
      {error && <p className="error-message">{error}</p>}
      <form onSubmit={handleSubmit}>
        {!isLogin && (
          <div className="form-group">
            <label htmlFor="name">Full Name:</label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="John Doe"
            />
          </div>
        )}
        <div className="form-group">
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="you@example.com"
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="••••••••"
          />
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Please wait...' : (isLogin ? 'Log In' : 'Register')}
        </button>
      </form>
      <p className="toggle-text">
        {isLogin ? "Don't have an account?" : 'Already have an account?'}
        <span className="toggle-auth" onClick={() => {
          setIsLogin(!isLogin);
          setError('');
          setMessage('');
        }}>
          {isLogin ? ' Register' : ' Log In'}
        </span>
      </p>
    </div>
  );
}

export default Auth;