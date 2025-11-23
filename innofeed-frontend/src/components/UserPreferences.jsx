import React, { useState } from 'react';
import './UserPreferences.css';

// These are the domains hardcoded in your ingest.py script
const ALL_DOMAINS = ["AI", "Robotics", "Quantum Computing", "Genetics", "Cybersecurity", "Blockchain"];

function UserPreferences({ userId, onUserIdChange, onSavePreferences }) {
  const [selectedDomains, setSelectedDomains] = useState(ALL_DOMAINS);
  const [currentUserId, setCurrentUserId] = useState(userId);

  const handleDomainChange = (event) => {
    const domain = event.target.value;
    setSelectedDomains((prev) =>
      prev.includes(domain) ? prev.filter((d) => d !== domain) : [...prev, domain]
    );
  };

  const handleSave = () => {
    onSavePreferences(selectedDomains);
  };

  const handleUserIdChange = (event) => {
    setCurrentUserId(event.target.value);
  };

  const handleSetUserId = () => {
    onUserIdChange(Number(currentUserId));
  };

  return (
    <div className="preferences-container">
      <h2>User Settings</h2>
      <div className="user-id-selector">
        <label>
          Enter User ID:
          <input
            type="number"
            value={currentUserId}
            onChange={handleUserIdChange}
          />
        </label>
        <button onClick={handleSetUserId}>Set User ID</button>
      </div>
      
      {/* Note: In a full app, you'd fetch available domains from the backend. 
      For this example, we're using a hardcoded list. */}
      <h3>Select Your Interests</h3>
      <p className="note">Note: This section is for a future feature. Your feed is currently personalized by the User ID.</p>
      <div className="domain-list">
        {ALL_DOMAINS.map((domain) => (
          <label key={domain}>
            <input
              type="checkbox"
              value={domain}
              checked={selectedDomains.includes(domain)}
              onChange={handleDomainChange}
              disabled // Disable for now as this feature is not yet fully implemented in the provided backend
            />
            {domain}
          </label>
        ))}
      </div>
      {/* <button onClick={handleSave}>Save Preferences</button> */}
    </div>
  );
}

export default UserPreferences;