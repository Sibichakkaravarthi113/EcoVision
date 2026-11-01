import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Car, Gauge, AlertCircle, Filter } from 'lucide-react';
import { useDemoMode } from '../context/DemoModeContext';
import { useLocationCtx } from '../context/LocationContext';
import { getTrafficCongestion, getTrafficSummary } from '../services/trafficApi';
import { resolveCoordinates, getCities } from '../data/indiaLocations';
import StatCard from '../components/StatCard';
import IndiaMap from '../components/IndiaMap';
import EcoChart from '../components/EcoChart';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorState from '../components/ErrorState';
import EmptyState from '../components/EmptyState';

const CONGESTION_LEVELS = ['Low', 'Moderate', 'Heavy', 'Severe'];

export default function TrafficCongestion() {
  const { demoMode } = useDemoMode();
  const { location, setLocation } = useLocationCtx();

  const [selectedLevel, setSelectedLevel] = useState('');
  const [records, setRecords] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const availableCities = useMemo(() => {
    return getCities(location.state, location.district);
  }, [location.state, location.district]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [resData, resSummary] = await Promise.all([
        getTrafficCongestion({
          state: location.state || undefined,
          city: location.city || undefined,
          level: selectedLevel || undefined,
          demo: demoMode ? true : undefined,
          limit: 100
        }),
        getTrafficSummary({
          state: location.state || undefined,
          demo: demoMode ? true : undefined
        })
      ]);

      setRecords(Array.isArray(resData) ? resData : (resData?.items || []));
      setSummary(resSummary);
    } catch (err) {
      setError(err.message || 'Failed to fetch traffic metrics');
    } finally {
      setLoading(false);
    }
  }, [location.state, location.city, selectedLevel, demoMode]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const mapCenter = useMemo(() => {
    return resolveCoordinates(location.city, location.state);
  }, [location.city, location.state]);

  const mapZoom = useMemo(() => {
    if (location.city) return 12;
    if (location.state) return 7;
    return 5;
  }, [location.city, location.state]);

  const getLevelMeta = (level) => {
    const l = (level || '').toLowerCase();
    if (l === 'severe') return { badge: 'badge-red', color: '#ef4444' };
    if (l === 'heavy') return { badge: 'badge-orange', color: '#f97316' };
    if (l === 'moderate') return { badge: 'badge-yellow', color: '#f59e0b' };
    return { badge: 'badge-green', color: '#10b981' };
  };

  const mapMarkers = useMemo(() => {
    if (records.length > 0) {
      return records
        .filter((r) => r.latitude && r.longitude)
        .map((r) => {
          const meta = getLevelMeta(r.congestion_level || r.level);
          return {
            lat: Number(r.latitude),
            lng: Number(r.longitude),
            label: `${r.road_name || 'Corridor'} (${r.avg_speed_kmh || 25} km/h)`,
            title: r.road_name || 'Traffic Monitoring Segment',
            value: r.vehicles_per_hour || 1800,
            unit: 'veh/hr',
            status: `${r.congestion_level || 'Moderate'} Congestion`,
            color: meta.color
          };
        });
    }

    if (summary) {
      const base = resolveCoordinates(location.city, location.state);
      return [
        {
          lat: base[0],
          lng: base[1],
          label: `${location.city || location.state || 'Urban'} Arterial Corridor`,
          title: 'Traffic Density Station',
          value: summary.avg_speed_kmh || 32,
          unit: 'km/h Speed',
          status: 'Normal Flow',
          color: '#10b981'
        }
      ];
    }
    return [];
  }, [records, summary, location.city, location.state]);

  // Bar chart: Vehicle count by road segment
  const vehicleChartData = useMemo(() => {
    if (records.length > 0) {
      return records.slice(0, 10).map((r) => ({
        name: r.road_name ? (r.road_name.length > 12 ? r.road_name.substring(0, 12) + '..' : r.road_name) : 'Road',
        vehicles: Number(r.vehicles_per_hour || 0)
      }));
    }
    return [];
  }, [records]);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header-text">
          <h1>Traffic Congestion</h1>
          <p>
            Real-time arterial traffic density, corridor travel velocities, and vehicle-induced emissions telemetry.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="filter-group">
          <Filter size={16} style={{ color: 'var(--text-muted)' }} />
          <span className="filter-label">Congestion Severity:</span>
          <select
            value={selectedLevel}
            onChange={(e) => setSelectedLevel(e.target.value)}
            className="form-select"
          >
            <option value="">All Congestion Levels</option>
            {CONGESTION_LEVELS.map((lvl) => (
              <option key={lvl} value={lvl}>
                {lvl}
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
              <option value="">All State Cities</option>
              {availableCities.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {loading && <LoadingSpinner message="Calculating vehicular flow rates and average transit velocities..." />}

      {!loading && error && (
        <ErrorState message={error} retry={fetchData} />
      )}

      {!loading && !error && records.length === 0 && !summary && (
        <EmptyState
          message="No traffic telemetry found for the selected area."
          suggestion="Select a metropolitan city or activate demo mode."
        />
      )}

      {!loading && !error && (
        <>
          {/* 3 Stat Cards */}
          <div className="grid-3">
            <StatCard
              title="Average Arterial Speed"
              value={summary?.avg_speed_kmh ?? '31.5'}
              unit="km/h"
              subtitle="Citywide transit velocity"
              icon={Gauge}
              color="#3b82f6"
            />

            <StatCard
              title="Average Vehicle Flow"
              value={summary?.avg_vehicles_per_hour ?? (Math.round(records.reduce((acc, r) => acc + (Number(r.vehicles_per_hour) || 0), 0) / (records.length || 1)) || '2,150')}
              unit="Vehicles/hr"
              subtitle="Peak corridor throughput"
              icon={Car}
              color="#8b5cf6"
            />

            <StatCard
              title="Critical Bottlenecks"
              value={summary?.severe_congestion_roads_count ?? records.filter(r => (r.congestion_level || '').toLowerCase() === 'severe' || (r.congestion_level || '').toLowerCase() === 'heavy').length}
              unit="Corridors"
              subtitle="Experiencing severe slowdowns"
              icon={AlertCircle}
              color="#ef4444"
            />
          </div>

          {/* Chart */}
          <EcoChart
            type="bar"
            data={vehicleChartData}
            xKey="name"
            yKey="vehicles"
            title="Vehicular Density by Major Transit Corridor"
            unit="Vehicles/hr"
            color="#8b5cf6"
            height={340}
          />

          {/* Map */}
          <IndiaMap
            markers={mapMarkers}
            center={mapCenter}
            zoom={mapZoom}
            height={400}
            title={`Arterial Road Network Congestion Levels — ${location.city || location.state || 'India'}`}
          />

          {/* Table */}
          <div className="data-card">
            <div className="data-card-header">
              <h3 className="data-card-title">Corridor Traffic Performance Registry</h3>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Showing {records.length} records
              </span>
            </div>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Road / Corridor Name</th>
                    <th>Vehicles Per Hour</th>
                    <th>Average Speed</th>
                    <th>Congestion Level</th>
                    <th>Peak Hour Window</th>
                  </tr>
                </thead>
                <tbody>
                  {records.slice(0, 25).map((r, i) => {
                    const meta = getLevelMeta(r.congestion_level || r.level);
                    return (
                      <tr key={r.id || `tc-${i}`}>
                        <td style={{ fontWeight: 600 }}>{r.road_name || `Corridor Segment ${i + 1}`}</td>
                        <td style={{ fontWeight: 600 }}>{Number(r.vehicles_per_hour || 0).toLocaleString()} veh/hr</td>
                        <td>{r.avg_speed_kmh} km/h</td>
                        <td>
                          <span className={`badge ${meta.badge}`}>
                            {r.congestion_level || r.level || 'Moderate'}
                          </span>
                        </td>
                        <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                          {r.peak_hour || '08:30 – 10:30'}
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
              Data Source: EcoVision Intelligent Transportation System (ITS) Synthetic Telemetry & Urban Transit Analytics.
            </span>
          </div>
        </>
      )}
    </div>
  );
}
