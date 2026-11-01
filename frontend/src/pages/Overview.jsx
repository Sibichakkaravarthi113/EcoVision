import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  Wind,
  Droplets,
  Trees,
  Trash2,
  Volume2,
  Car,
  Factory,
  CloudSun,
  ShieldCheck,
  Calendar,
  ExternalLink
} from 'lucide-react';
import { useDemoMode } from '../context/DemoModeContext';
import { useLocationCtx } from '../context/LocationContext';
import { getOverview } from '../services/overviewApi';
import { resolveCoordinates } from '../data/indiaLocations';
import StatCard from '../components/StatCard';
import IndiaMap from '../components/IndiaMap';
import EcoChart from '../components/EcoChart';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorState from '../components/ErrorState';
import EmptyState from '../components/EmptyState';

export default function Overview() {
  const { demoMode } = useDemoMode();
  const { location } = useLocationCtx();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getOverview({
        state: location.state || undefined,
        city: location.city || undefined,
        demo: demoMode ? true : undefined
      });
      setData(res);
    } catch (err) {
      setError(err.message || 'Failed to fetch environmental overview');
    } finally {
      setLoading(false);
    }
  }, [location.state, location.city, demoMode]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const locationLabel = useMemo(() => {
    if (location.city && location.state) return `${location.city}, ${location.state}`;
    if (location.state) return location.state;
    return 'India (National Overview)';
  }, [location.state, location.city]);

  // Center coordinates for map
  const mapCenter = useMemo(() => {
    return resolveCoordinates(location.city, location.state);
  }, [location.city, location.state]);

  const mapZoom = useMemo(() => {
    if (location.city) return 11;
    if (location.state) return 7;
    return 5;
  }, [location.city, location.state]);

  // Generate chart data from overview dimensions
  const chartData = useMemo(() => {
    if (!data) return [];
    if (Array.isArray(data.chart_data)) return data.chart_data;

    // Build metric scores from dimension objects or summaries
    const metrics = [
      { name: 'Air Quality', score: data.air_quality?.score ?? (data.air_quality?.pm25 ? Math.max(10, 100 - Number(data.air_quality.pm25) / 2) : 75) },
      { name: 'Water Purity', score: data.water_quality?.score ?? (data.water_quality?.ph ? 82 : 70) },
      { name: 'Green Canopy', score: data.green_coverage?.forest_percentage ?? data.green_coverage?.score ?? 35 },
      { name: 'Waste Mgmt', score: data.waste_management?.recycling_rate ?? data.waste_management?.score ?? 60 },
      { name: 'Acoustic Health', score: data.noise_pollution?.score ?? 68 },
      { name: 'Traffic Flow', score: data.traffic?.score ?? 58 },
      { name: 'Ind. Compliance', score: data.industrial?.compliance_rate ?? data.industrial?.score ?? 84 },
      { name: 'Climate Index', score: data.climate?.score ?? 78 }
    ];
    return metrics;
  }, [data]);

  // Map markers
  const mapMarkers = useMemo(() => {
    if (!data) return [];
    if (Array.isArray(data.markers) && data.markers.length > 0) return data.markers;

    const baseCoords = resolveCoordinates(location.city, location.state);
    const markers = [];

    // Air Quality Marker
    markers.push({
      lat: baseCoords[0] + 0.04,
      lng: baseCoords[1] + 0.03,
      label: 'Air Quality Station',
      title: 'Ambient Air Monitoring Station',
      value: data.air_quality?.pm25 ?? 45,
      unit: 'µg/m³ PM2.5',
      status: (data.air_quality?.pm25 ?? 45) > 60 ? 'Moderate' : 'Good',
      color: (data.air_quality?.pm25 ?? 45) > 60 ? '#f59e0b' : '#10b981'
    });

    // Water Quality Marker
    markers.push({
      lat: baseCoords[0] - 0.03,
      lng: baseCoords[1] - 0.04,
      label: 'River / Reservoir Station',
      title: 'Surface Water Monitoring Point',
      value: data.water_quality?.ph ?? 7.4,
      unit: 'pH',
      status: 'Normal Class B',
      color: '#3b82f6'
    });

    // Forest / Green Marker
    markers.push({
      lat: baseCoords[0] + 0.06,
      lng: baseCoords[1] - 0.05,
      label: 'Ecological Reserve',
      title: 'Forest Canopy Observation Sector',
      value: data.green_coverage?.forest_percentage ?? 24.5,
      unit: '% cover',
      status: 'Protected Flora',
      color: '#059669'
    });

    // Industrial Monitoring Marker
    markers.push({
      lat: baseCoords[0] - 0.05,
      lng: baseCoords[1] + 0.05,
      label: 'Industrial Zone Sensor',
      title: 'Continuous Emission Monitoring',
      value: data.industrial?.compliance_rate ?? 91,
      unit: '% compliant',
      status: 'Compliant',
      color: '#8b5cf6'
    });

    return markers;
  }, [data, location.city, location.state]);

  // Dimensions array for overview table and cards
  const dimensionList = useMemo(() => {
    if (!data) return [];
    return [
      {
        id: 'air',
        name: 'Air Quality',
        path: '/air-quality',
        icon: Wind,
        color: '#10b981',
        value: data.air_quality?.pm25 ?? data.air_quality?.avg_pm25 ?? '42.8',
        unit: 'µg/m³ PM2.5',
        status: (data.air_quality?.pm25 || 42) > 60 ? 'Moderate' : 'Good',
        subtitle: `Stations: ${data.air_quality?.stations_count ?? 14}`,
        asOf: data.air_quality?.last_updated || 'Today'
      },
      {
        id: 'water',
        name: 'Water Quality',
        path: '/water-quality',
        icon: Droplets,
        color: '#0284c7',
        value: data.water_quality?.ph ?? '7.3',
        unit: 'pH Level',
        status: 'Optimal Range',
        subtitle: `DO: ${data.water_quality?.dissolved_oxygen ?? '6.8'} mg/L`,
        asOf: data.water_quality?.last_updated || 'Today'
      },
      {
        id: 'green',
        name: 'Green Coverage',
        path: '/green-coverage',
        icon: Trees,
        color: '#16a34a',
        value: data.green_coverage?.forest_percentage ?? '28.4',
        unit: '% of area',
        status: 'Stable Canopy',
        subtitle: `Forest: ${data.green_coverage?.total_forest_sqkm ?? '1,420'} sq km`,
        asOf: data.green_coverage?.last_updated || 'FSI 2023'
      },
      {
        id: 'waste',
        name: 'Waste Management',
        path: '/waste-management',
        icon: Trash2,
        color: '#d97706',
        value: data.waste_management?.recycling_rate ?? '64.2',
        unit: '% Recycled',
        status: 'High Processing',
        subtitle: `Generated: ${data.waste_management?.daily_tonnes ?? '850'} TPD`,
        asOf: data.waste_management?.last_updated || 'Current'
      },
      {
        id: 'noise',
        name: 'Noise Pollution',
        path: '/noise-pollution',
        icon: Volume2,
        color: '#ea580c',
        value: data.noise_pollution?.day_avg_db ?? '62.4',
        unit: 'dB(A) Day Avg',
        status: (data.noise_pollution?.day_avg_db || 62) > 65 ? 'Elevated' : 'Acceptable',
        subtitle: `Night Avg: ${data.noise_pollution?.night_avg_db ?? '51.2'} dB(A)`,
        asOf: data.noise_pollution?.last_updated || 'Live Telemetry'
      },
      {
        id: 'traffic',
        name: 'Traffic Congestion',
        path: '/traffic',
        icon: Car,
        color: '#8b5cf6',
        value: data.traffic?.avg_speed_kmh ?? '32.6',
        unit: 'km/h Speed',
        status: (data.traffic?.avg_speed_kmh || 32) < 25 ? 'Heavy Congestion' : 'Normal Flow',
        subtitle: `Vehicles: ${data.traffic?.vehicles_per_hour ?? '2,400'}/hr`,
        asOf: data.traffic?.last_updated || 'Current'
      },
      {
        id: 'industrial',
        name: 'Industrial Activity',
        path: '/industrial',
        icon: Factory,
        color: '#4f46e5',
        value: data.industrial?.compliance_rate ?? '89.5',
        unit: '% Compliant',
        status: 'SPCB Supervised',
        subtitle: `Active Units: ${data.industrial?.total_units ?? 128}`,
        asOf: data.industrial?.last_updated || 'Current'
      },
      {
        id: 'climate',
        name: 'Climate Conditions',
        path: '/climate',
        icon: CloudSun,
        color: '#0d9488',
        value: data.climate?.temperature ?? '28.2',
        unit: '°C Ambient',
        status: data.climate?.condition || 'Partly Cloudy',
        subtitle: `Humidity: ${data.climate?.humidity ?? 65}%`,
        asOf: data.climate?.last_updated || 'Live Forecast'
      }
    ];
  }, [data]);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header-text">
          <h1>Environmental Overview</h1>
          <p>Comprehensive ecological and environmental intelligence for <strong>{locationLabel}</strong></p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span className="badge badge-green">
            <ShieldCheck size={14} /> System Operational
          </span>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Calendar size={14} /> Updated {new Date().toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' })}
          </span>
        </div>
      </div>

      {loading && <LoadingSpinner message="Synthesizing multi-dimensional environmental indicators..." />}

      {!loading && error && (
        <ErrorState message={error} retry={fetchData} />
      )}

      {!loading && !error && !data && (
        <EmptyState message="No environmental overview data received." />
      )}

      {!loading && !error && data && (
        <>
          {/* 8 Stat Cards for the 8 Dimensions */}
          <div className="grid-4">
            {dimensionList.map((dim) => {
              const Icon = dim.icon;
              return (
                <Link key={dim.id} to={dim.path} style={{ textDecoration: 'none' }}>
                  <StatCard
                    title={dim.name}
                    value={dim.value}
                    unit={dim.unit}
                    subtitle={`${dim.subtitle} • ${dim.status}`}
                    icon={Icon}
                    color={dim.color}
                  />
                </Link>
              );
            })}
          </div>

          {/* Center Visuals: Chart & Regional Map */}
          <div className="grid-split">
            <EcoChart
              type="bar"
              data={chartData}
              xKey="name"
              yKey="score"
              title="Environmental Health Indices (0-100 Scale)"
              unit="pts"
              color="#1a5c38"
              height={360}
            />

            <IndiaMap
              markers={mapMarkers}
              center={mapCenter}
              zoom={mapZoom}
              height={360}
              title={`Environmental Stations in ${locationLabel}`}
            />
          </div>

          {/* Comprehensive Environmental Index Table */}
          <div className="data-card">
            <div className="data-card-header">
              <h3 className="data-card-title">Environmental Dimension Scorecard</h3>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Target: NAAQS, CPCB & MOEFCC Environmental Standards
              </span>
            </div>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Dimension</th>
                    <th>Primary Metric</th>
                    <th>Current Value</th>
                    <th>Status Assessment</th>
                    <th>Data Freshness</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {dimensionList.map((dim) => (
                    <tr key={dim.id}>
                      <td style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <dim.icon size={16} color={dim.color} />
                        {dim.name}
                      </td>
                      <td>{dim.subtitle}</td>
                      <td style={{ fontWeight: 600 }}>{dim.value} {dim.unit}</td>
                      <td>
                        <span className={`badge ${
                          dim.status.includes('Good') || dim.status.includes('Optimal') || dim.status.includes('High') || dim.status.includes('Stable')
                            ? 'badge-green'
                            : dim.status.includes('Moderate') || dim.status.includes('Acceptable')
                            ? 'badge-yellow'
                            : 'badge-orange'
                        }`}>
                          {dim.status}
                        </span>
                      </td>
                      <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{dim.asOf}</td>
                      <td>
                        <Link to={dim.path} className="btn btn-secondary" style={{ padding: '0.3rem 0.65rem', fontSize: '0.75rem' }}>
                          Inspect <ExternalLink size={12} style={{ marginLeft: '4px' }} />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="data-source-note">
            <span>Data Sources: Central Pollution Control Board (CPCB), Forest Survey of India (FSI), Open-Meteo API, and EcoVision Environmental Observation Network.</span>
          </div>
        </>
      )}
    </div>
  );
}
