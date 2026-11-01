import React from 'react';

export default function LoadingSpinner({ message = 'Loading environmental data...' }) {
  return (
    <div className="spinner-container">
      <div className="spinner" />
      <p style={{ fontSize: '0.9rem', fontWeight: 500 }}>{message}</p>
    </div>
  );
}
