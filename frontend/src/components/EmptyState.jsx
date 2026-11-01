import React from 'react';
import { Database } from 'lucide-react';

export default function EmptyState({
  message = 'No environmental records found for the selected filters.',
  suggestion = 'Try adjusting your state, district, or date range filters, or enable Demo Mode to view simulated data.',
  icon: Icon = Database
}) {
  return (
    <div className="state-box">
      <div className="state-icon-box empty">
        <Icon size={28} />
      </div>
      <div style={{ maxWidth: '440px' }}>
        <h4 style={{ marginBottom: '0.4rem', fontSize: '1rem' }}>No Data Available</h4>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
          {message}
        </p>
        {suggestion && (
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {suggestion}
          </p>
        )}
      </div>
    </div>
  );
}
