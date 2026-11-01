import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

export default function StatCard({
  title,
  value,
  unit = '',
  subtitle = '',
  icon: Icon,
  color = 'var(--primary)',
  trend = null,
  trendDirection = 'neutral'
}) {
  return (
    <div className="stat-card">
      <div className="stat-card-content">
        <div className="stat-card-title">{title}</div>
        <div className="stat-card-value">
          {value !== undefined && value !== null ? value : '—'}
          {unit && <span className="stat-card-unit">{unit}</span>}
        </div>
        {subtitle && <div className="stat-card-subtitle">{subtitle}</div>}
        {trend && (
          <div className={`stat-card-trend ${trendDirection === 'down' ? 'trend-down' : 'trend-up'}`}>
            {trendDirection === 'down' ? <TrendingDown size={13} /> : <TrendingUp size={13} />}
            <span>{trend}</span>
          </div>
        )}
      </div>

      {Icon && (
        <div
          className="stat-card-icon"
          style={{
            backgroundColor: `${color}15`,
            color: color
          }}
        >
          <Icon size={24} />
        </div>
      )}
    </div>
  );
}
