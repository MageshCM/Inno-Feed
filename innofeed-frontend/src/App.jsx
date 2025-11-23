// src/App.jsx
import React, { useState } from 'react';
import Auth from './components/Auth';
import FeedPage from './components/FeedPage';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userId, setUserId] = useState(null);
  const [userName, setUserName] = useState(null);

  // Configure your backend API URL
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleAuthSuccess = (id, name) => {
    setUserId(id);
    setUserName(name);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setUserId(null);
    setUserName(null);
    setIsAuthenticated(false);
  };

  return (
    <div className="App">
      {!isAuthenticated ? (
        <Auth onAuthSuccess={handleAuthSuccess} API_BASE_URL={API_BASE_URL} />
      ) : (
        <FeedPage
          userId={userId}
          userName={userName}
          onLogout={handleLogout}
          API_BASE_URL={API_BASE_URL}
        />
      )}
    </div>
  );
}

export default App;