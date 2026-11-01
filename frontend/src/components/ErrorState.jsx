import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export default function ErrorState({
  message = 'Failed to load data. The backend server might be offline or an unexpected error occurred.',
  retry = null
}) {
  return (
    <div className="state-box">
      <div className="state-icon-box error">
        <AlertTriangle size={28} />
      </div>
      <div style={{ maxWidth: '480px' }}>
        <h4 style={{ color: 'var(--accent-red)', marginBottom: '0.4rem', fontSize: '1.05rem' }}>
          Unable to Load Data
        </h4>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          {message}
        </p>
      </div>
      {retry && (
        <button className="btn btn-secondary" onClick={retry} style={{ marginTop: '0.5rem' }}>
          <RefreshCw size={15} />
          Retry Request
        </button>
      )}
    </div>
  );
}
