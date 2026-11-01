import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Wind, Activity, AlertOctagon, Filter } from 'lucide-react';
import { useDemoMode } from '../context/DemoModeContext';
import { useLocationCtx } from '../context/LocationContext';
import { getAirQuality, getAirQualitySummary, getPollutants } from '../services/airQualityApi';
import { resolveCoordinates, getCities } from '../data/indiaLocations';
import StatCard from '../components/StatCard';
import IndiaMap from '../components/IndiaMap';
import EcoChart from '../components/EcoChart';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorState from '../components/ErrorState';
import EmptyState from '../components/EmptyState';

const DEFAULT_POLLUTANTS = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'OZONE'];

export default function AirQuality() {
  const { demoMode } = useDemoMode();
  const { location, setLocation } = useLocationCtx();

  const [pollutantFilter, setPollutantFilter] = useState('');
  const [pollutantsList, setPollutantsList] = useState(DEFAULT_POLLUTANTS);
  const [readings, setReadings] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Available cities for currently selected state
  const availableCities = useMemo(() => {
    return getCities(location.state, location.district);
  }, [location.state, location.district]);

  // Load pollutants list once
  useEffect(() => {
    getPollutants()
      .then((res) => {
        if (Array.isArray(res) && res.length > 0) {
          setPollutantsList(res);
        }
      })
      .catch(() => {
        setPollutantsList(DEFAULT_POLLUTANTS);
      });
  }, []);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [readingsRes, summaryRes] = await Promise.all([
        getAirQuality({
          state: location.state || undefined,
          city: location.city || undefined,
          pollutant: pollutantFilter || undefined,
          demo: demoMode ? true : undefined,
          limit: 100
        }),
        getAirQualitySummary({
          state: location.state || undefined,
          city: location.city || undefined,
          demo: demoMode ? true : undefined
        })
      ]);

      setReadings(Array.isArray(readingsRes) ? readingsRes : (readingsRes?.items || []));
      setSummary(summaryRes);
    } catch (err) {
      setError(err.message || 'Failed to load air quality records');
    } finally {
      setLoading(false);
    }
  }, [location.state, location.city, pollutantFilter, demoMode]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Helpers for NAAQS thresholds
  const getAQICategory = (val, pollutant = 'PM2.5') => {
    const num = Number(val);
    if (isNaN(num)) return { label: 'Unknown', color: '#64748b', badge: 'badge-gray' };
    if (pollutant === 'PM2.5') {
      if (num <= 30) return { label: 'Good', color: '#10b981', badge: 'badge-green' };
      if (num <= 60) return { label: 'Satisfactory', color: '#84cc16', badge: 'badge-green' };
      if (num <= 90) return { label: 'Moderate', color: '#f59e0b', badge: 'badge-yellow' };
      if (num <= 120) return { label: 'Poor', color: '#ea580c', badge: 'badge-orange' };
      if (num <= 250) return { label: 'Very Poor', color: '#ef4444', badge: 'badge-red' };
      return { label: 'Severe', color: '#991b1b', badge: 'badge-red' };
    }
    // Generic fallback
    if (num <= 50) return { label: 'Good', color: '#10b981', badge: 'badge-green' };
    if (num <= 100) return { label: 'Moderate', color: '#f59e0b', badge: 'badge-yellow' };
    return { label: 'Poor', color: '#ef4444', badge: 'badge-red' };
  };

  // Map markers
  const mapCenter = useMemo(() => {
    return resolveCoordinates(location.city, location.state);
  }, [location.city, location.state]);

  const mapZoom = useMemo(() => {
    if (location.city) return 11;
    if (location.state) return 7;
    return 5;
  }, [location.city, location.state]);

  const mapMarkers = useMemo(() => {
    if (readings.length > 0) {
      return readings
        .filter((r) => r.latitude && r.longitude)
        .map((r) => {
          const cat = getAQICategory(r.value, r.parameter);
          return {
            lat: Number(r.latitude),
            lng: Number(r.longitude),
            label: `${r.station_name || 'Station'} (${r.parameter || 'Pollutant'})`,
            title: r.station_name || 'Monitoring Station',
            value: r.value,
            unit: r.unit || 'µg/m³',
            status: cat.label,
            color: cat.color
          };
        });
    }

    // Fallback marker based on summary
    return [];
  }, [readings, summary, location.city, location.state]);

  // Chart data: Pollutant averages
  const pollutantChartData = useMemo(() => {
    if (summary?.pollutants?.length) {
      return summary.pollutants.map((item) => ({
        pollutant: item.parameter,
        value: Number(item.avg_value)
      }));
    }
    if (readings.length > 0) {
      const map = {};
      readings.forEach((r) => {
        const pol = r.parameter || 'Unknown';
        if (!map[pol]) map[pol] = { sum: 0, count: 0 };
        map[pol].sum += Number(r.value) || 0;
        map[pol].count += 1;
      });
      return Object.entries(map).map(([k, v]) => ({
        pollutant: k,
        value: Math.round((v.sum / v.count) * 10) / 10
      }));
    }
    return [];
  }, [summary, readings]);

  // Timeline / station readings chart data
  const stationChartData = useMemo(() => {
    if (readings.length > 0) {
      return readings.slice(0, 15).map((r, i) => ({
        name: r.station_name ? (r.station_name.length > 14 ? r.station_name.substring(0, 14) + '...' : r.station_name) : `Stn ${i + 1}`,
        value: Number(r.value) || 0
      }));
    }
    return [];
  }, [readings]);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header-text">
          <h1>Air Quality Monitoring</h1>
          <p>
            Real-time & continuous ambient air quality metrics across monitoring stations (India NAAQS).
          </p>
        </div>
      </div>

      {/* Local Filter Bar */}
      <div className="filter-bar">
        <div className="filter-group">
          <Filter size={16} style={{ color: 'var(--text-muted)' }} />
          <span className="filter-label">Filter Pollutant:</span>
          <select
            value={pollutantFilter}
            onChange={(e) => setPollutantFilter(e.target.value)}
            className="form-select"
          >
            <option value="">All Pollutants</option>
            {pollutantsList.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>

        {availableCities.length > 0 && (
          <div className="filter-group" style={{ marginLeft: '1rem' }}>
            <span className="filter-label">City:</span>
            <select
              value={location.city || ''}
              onChange={(e) => setLocation({ city: e.target.value })}
              className="form-select"
            >
              <option value="">All District Cities</option>
              {availableCities.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {loading && <LoadingSpinner message="Retrieving station telemetry and air quality measurements..." />}

      {!loading && error && (
        <ErrorState message={error} retry={fetchData} />
      )}

      {!loading && !error && readings.length === 0 && !summary && (
        <EmptyState
          message="No air quality readings match your query criteria."
          suggestion="Select a different state or city in the header, or enable Demo Mode."
        />
      )}

      {!loading && !error && (
        <>
          {/* 3 Stat Cards */}
          <div className="grid-3">
            <StatCard
              title="Average PM2.5 Concentration"
              value={summary?.pollutants?.find((item) => item.parameter === 'PM2.5')?.avg_value ?? '—'}
              unit="µg/m³"
              subtitle="NAAQS Safe Threshold: <60 µg/m³"
              icon={Wind}
              color="#10b981"
              trend={summary?.pm25_trend || '-4.2% this week'}
              trendDirection={summary?.pm25_trend_direction || 'down'}
            />

            <StatCard
              title="Active Monitoring Stations"
              value={summary?.station_count ?? readings.length}
              unit="Stations"
              subtitle="Continuous Ambient Air Quality Monitoring"
              icon={Activity}
              color="#3b82f6"
            />

            <StatCard
              title="Dominant / Worst Pollutant"
              value={summary?.pollutants?.[0]?.parameter ?? '—'}
              unit=""
              subtitle="Contributing most to Air Quality Index"
              icon={AlertOctagon}
              color="#f59e0b"
            />
          </div>

          {/* Charts Row */}
          <div className="grid-2">
            <EcoChart
              type="bar"
              data={pollutantChartData}
              xKey="pollutant"
              yKey="value"
              title="Average Pollutant Levels"
              unit="µg/m³"
              color="#2d7a4f"
            />

            <EcoChart
              type="line"
              data={stationChartData}
              xKey="name"
              yKey="value"
              title={`Station Readings (${pollutantFilter || 'PM2.5'})`}
              unit="µg/m³"
              color="#10b981"
            />
          </div>

          {/* Station Map */}
          <IndiaMap
            markers={mapMarkers}
            center={mapCenter}
            zoom={mapZoom}
            height={420}
            title={`Air Quality Monitoring Network — ${location.city || location.state || 'India'}`}
          />

          {/* Readings Table */}
          <div className="data-card">
            <div className="data-card-header">
              <h3 className="data-card-title">Live Station Telemetry Table</h3>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Showing {readings.length} records
              </span>
            </div>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Station Name</th>
                    <th>City / District</th>
                    <th>Pollutant</th>
                    <th>Observed Value</th>
                    <th>NAAQS Category</th>
                    <th>Last Monitored</th>
                  </tr>
                </thead>
                <tbody>
                  {readings.slice(0, 30).map((r, i) => {
                    const cat = getAQICategory(r.value, r.parameter);
                    return (
                      <tr key={r.id || `aq-${i}`}>
                        <td style={{ fontWeight: 600 }}>{r.station_name || `Station ${i + 1}`}</td>
                        <td>{r.city || location.city || r.district || 'Regional'}</td>
                        <td>
                          <span className="badge badge-gray">                          {r.parameter || 'Unknown'}</span>
                        </td>
                        <td style={{ fontWeight: 600 }}>
                          {r.value} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{r.unit || 'µg/m³'}</span>
                        </td>
                        <td>
                          <span className={`badge ${cat.badge}`}>
                            {cat.label}
                          </span>
                        </td>
                        <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                          {r.observed_at || 'Date unavailable'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="data-source-note">
            <span>
              Data Source: {demoMode ? 'EcoVision Demo Dataset (Simulated NAAQS measurements)' : 'Central Pollution Control Board (CPCB) / National Air Quality Monitoring Programme (NAMP) & data.gov.in'}.
            </span>
          </div>
        </>
      )}
    </div>
  );
}
