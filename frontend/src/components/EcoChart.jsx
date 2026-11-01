import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

const DEFAULT_COLORS = ['#2d7a4f', '#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444'];

function CustomTooltip({ active, payload, label, unit }) {
  if (active && payload && payload.length) {
    return (
      <div
        style={{
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          padding: '8px 12px',
          boxShadow: 'var(--shadow-md)',
          fontSize: '0.85rem'
        }}
      >
        <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>
          {label}
        </p>
        {payload.map((entry, index) => (
          <div key={`item-${index}`} style={{ display: 'flex', alignItems: 'center', gap: 6, margin: '2px 0' }}>
            <span
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: entry.color || entry.fill,
                display: 'inline-block'
              }}
            />
            <span style={{ color: 'var(--text-secondary)' }}>{entry.name}:</span>
            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
              {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value} {unit}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
}

export default function EcoChart({
  type = 'bar',
  data = [],
  xKey = 'name',
  yKey = 'value',
  keys = null,
  color = '#2d7a4f',
  colors = DEFAULT_COLORS,
  title = '',
  unit = '',
  height = 320
}) {
  if (!data || data.length === 0) {
    return (
      <div className="data-card" style={{ height: `${height}px`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No data available to display chart</p>
      </div>
    );
  }

  const renderChart = () => {
    if (type === 'line') {
      return (
        <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 25 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" opacity={0.6} />
          <XAxis
            dataKey={xKey}
            stroke="var(--text-muted)"
            fontSize={12}
            tickLine={false}
            dy={8}
            interval="preserveStartEnd"
          />
          <YAxis
            stroke="var(--text-muted)"
            fontSize={12}
            tickLine={false}
            dx={-8}
          />
          <Tooltip content={<CustomTooltip unit={unit} />} />
          {keys && keys.length > 1 && <Legend wrapperStyle={{ paddingTop: '10px' }} />}
          {keys && keys.length > 0 ? (
            keys.map((k, idx) => (
              <Line
                key={k}
                type="monotone"
                dataKey={k}
                stroke={colors[idx % colors.length]}
                strokeWidth={2.5}
                dot={{ r: 3, fill: colors[idx % colors.length] }}
                activeDot={{ r: 6 }}
              />
            ))
          ) : (
            <Line
              type="monotone"
              dataKey={yKey}
              stroke={color}
              strokeWidth={2.5}
              dot={{ r: 3, fill: color }}
              activeDot={{ r: 6 }}
            />
          )}
        </LineChart>
      );
    }

    if (type === 'area') {
      return (
        <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 25 }}>
          <defs>
            <linearGradient id="ecoAreaGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.4} />
              <stop offset="95%" stopColor={color} stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" opacity={0.6} />
          <XAxis
            dataKey={xKey}
            stroke="var(--text-muted)"
            fontSize={12}
            tickLine={false}
            dy={8}
          />
          <YAxis
            stroke="var(--text-muted)"
            fontSize={12}
            tickLine={false}
            dx={-8}
          />
          <Tooltip content={<CustomTooltip unit={unit} />} />
          {keys && keys.length > 1 && <Legend wrapperStyle={{ paddingTop: '10px' }} />}
          {keys && keys.length > 0 ? (
            keys.map((k, idx) => (
              <Area
                key={k}
                type="monotone"
                dataKey={k}
                stroke={colors[idx % colors.length]}
                fill={colors[idx % colors.length]}
                fillOpacity={0.25}
              />
            ))
          ) : (
            <Area
              type="monotone"
              dataKey={yKey}
              stroke={color}
              fillOpacity={1}
              fill="url(#ecoAreaGradient)"
            />
          )}
        </AreaChart>
      );
    }

    // Default: Bar Chart
    return (
      <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 25 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" opacity={0.6} />
        <XAxis
          dataKey={xKey}
          stroke="var(--text-muted)"
          fontSize={12}
          tickLine={false}
          dy={8}
        />
        <YAxis
          stroke="var(--text-muted)"
          fontSize={12}
          tickLine={false}
          dx={-8}
        />
        <Tooltip content={<CustomTooltip unit={unit} />} />
        {keys && keys.length > 1 && <Legend wrapperStyle={{ paddingTop: '10px' }} />}
        {keys && keys.length > 0 ? (
          keys.map((k, idx) => (
            <Bar
              key={k}
              dataKey={k}
              fill={colors[idx % colors.length]}
              radius={[4, 4, 0, 0]}
            />
          ))
        ) : (
          <Bar
            dataKey={yKey}
            fill={color}
            radius={[4, 4, 0, 0]}
          />
        )}
      </BarChart>
    );
  };

  return (
    <div className="data-card">
      {title && (
        <div className="data-card-header">
          <h3 className="data-card-title">{title}</h3>
          {unit && <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>({unit})</span>}
        </div>
      )}
      <div style={{ width: '100%', height: `${height}px` }}>
        <ResponsiveContainer width="100%" height="100%">
          {renderChart()}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
