// src/components/FeedPage.jsx
import React, { useState, useEffect } from 'react';
import Feed from './Feed';
import './FeedPage.css';

function FeedPage({ userId, userName, onLogout, API_BASE_URL }) {
  const [feed, setFeed] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [availableDomains, setAvailableDomains] = useState([]);
  const [userDomainIds, setUserDomainIds] = useState([]);

  // Fetch available domains from backend
  const fetchDomains = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/domains`);
      if (!response.ok) throw new Error('Failed to fetch domains.');
      const data = await response.json();
      setAvailableDomains(data);
    } catch (e) {
      setError('Could not load domains.');
    }
  };

  // Fetch the personalized feed
  const fetchFeed = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/feed/${userId}`);
      if (!response.ok) throw new Error('Failed to fetch feed.');
      const data = await response.json();
      setFeed(data.feed);
    } catch (e) {
      setError('Failed to fetch feed. Please check the backend connection.');
    } finally {
      setIsLoading(false);
    }
  };

  // Save user preferences
  const savePreferences = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/set-preferences/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain_ids: userDomainIds }),
      });
      if (!response.ok) throw new Error('Failed to save preferences.');
      alert('Preferences saved!');
      fetchFeed(); // Refresh feed after saving
    } catch (e) {
      setError('Failed to save preferences.');
    }
  };

  const handleDomainChange = (domainId) => {
    setUserDomainIds((prev) =>
      prev.includes(domainId) ? prev.filter((id) => id !== domainId) : [...prev, domainId]
    );
  };

  useEffect(() => {
    fetchDomains();
  }, []);

  useEffect(() => {
    if (userId) {
      fetchFeed();
    }
  }, [userId, userDomainIds]);

  return (
    <div className="feed-page-container">
      <div className="user-info">
        <h3>Welcome back, {userName || `User ${userId}`}!</h3>

        <button onClick={onLogout}>Logout</button>
      </div>
      <div className="preferences-section">
        <h3>Select Your Interests</h3>
        <div className="domain-list">
          {availableDomains.map((domain) => (
            <label key={domain.id}>
              <input
                type="checkbox"
                checked={userDomainIds.includes(domain.id)}
                onChange={() => handleDomainChange(domain.id)}
              />
              {domain.name}
            </label>
          ))}
        </div>
        <button className="save-button" onClick={savePreferences}>Save Preferences</button>
      </div>
      <hr />
      {isLoading && <p>Loading your feed...</p>}
      {error && <p className="error">{error}</p>}
      {!isLoading && !error && <Feed feedData={feed} />}
    </div>
  );
}

export default FeedPage;