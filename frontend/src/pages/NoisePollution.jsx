import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Volume2, Moon, AlertTriangle, Filter } from 'lucide-react';
import { useDemoMode } from '../context/DemoModeContext';
import { useLocationCtx } from '../context/LocationContext';
import { getNoisePollution, getNoiseSummary } from '../services/noiseApi';
import { resolveCoordinates, getCities } from '../data/indiaLocations';
import StatCard from '../components/StatCard';
import IndiaMap from '../components/IndiaMap';
import EcoChart from '../components/EcoChart';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorState from '../components/ErrorState';
import EmptyState from '../components/EmptyState';

const LOCATION_TYPES = ['Industrial', 'Commercial', 'Residential', 'Silence Zone'];

const CPCB_LIMITS = {
  Industrial: { day: 75, night: 70 },
  Commercial: { day: 65, night: 55 },
  Residential: { day: 55, night: 45 },
  'Silence Zone': { day: 50, night: 40 }
};

export default function NoisePollution() {
  const { demoMode } = useDemoMode();
  const { location, setLocation } = useLocationCtx();

  const [selectedType, setSelectedType] = useState('');
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
        getNoisePollution({
          state: location.state || undefined,
          city: location.city || undefined,
          locationType: selectedType || undefined,
          demo: demoMode ? true : undefined,
          limit: 100
        }),
        location.city
          ? getNoiseSummary({
              state: location.state || undefined,
              city: location.city,
              demo: demoMode ? true : undefined
            })
          : Promise.resolve(null)
      ]);

      setRecords(Array.isArray(resData) ? resData : (resData?.items || []));
      setSummary(resSummary);
    } catch (err) {
      setError(err.message || 'Failed to load noise monitoring data');
    } finally {
      setLoading(false);
    }
  }, [location.state, location.city, selectedType, demoMode]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const mapCenter = useMemo(() => {
    return resolveCoordinates(location.city, location.state);
  }, [location.city, location.state]);

  const mapZoom = useMemo(() => {
    if (location.city) return 11;
    if (location.state) return 7;
    return 5;
  }, [location.city, location.state]);

  // Check CPCB exceedance
  const checkExceedance = (type, dayVal) => {
    const limits = CPCB_LIMITS[type] || CPCB_LIMITS.Commercial;
    const day = Number(dayVal) || 0;
    const exceeds = day > limits.day;
    return {
      exceeds,
      limit: limits.day,
      label: exceeds ? 'Exceeds Standard' : 'Within Standard',
      badge: exceeds ? 'badge-red' : 'badge-green',
      color: exceeds ? '#ef4444' : '#10b981'
    };
  };

  const mapMarkers = useMemo(() => {
    if (records.length > 0) {
      return records
        .filter((r) => r.latitude && r.longitude)
        .map((r) => {
          const evalObj = checkExceedance(r.location_type || r.zone, r.day_db);
          return {
            lat: Number(r.latitude),
            lng: Number(r.longitude),
            label: `${r.station_name || r.location || 'Noise Sensor'} (${r.day_db} dB)`,
            title: r.station_name || r.location || 'Acoustic Monitoring Sensor',
            value: r.day_db,
            unit: 'dB(A) Day',
            status: evalObj.label,
            color: evalObj.color
          };
        });
    }

    if (summary) {
      const base = resolveCoordinates(location.city, location.state);
      return [
        {
          lat: base[0],
          lng: base[1],
          label: `${location.city || location.state || 'Urban'} Ambient Acoustic Station`,
          title: 'Ambient Acoustic Sensor',
          value: summary.levels?.[0]?.avg_day_db || 0,
          unit: 'dB(A) Day',
          status: 'Within Standard',
          color: '#10b981'
        }
      ];
    }
    return [];
  }, [records, summary, location.city, location.state]);

  // Day vs Night levels chart
  const dayNightChartData = useMemo(() => {
    if (summary?.zone_breakdown) {
      return summary.zone_breakdown;
    }
    if (records.length > 0) {
      const typeGroups = {};
      records.forEach((r) => {
        const type = r.location_type || r.zone || 'Commercial';
        if (!typeGroups[type]) typeGroups[type] = { daySum: 0, nightSum: 0, count: 0 };
        typeGroups[type].daySum += Number(r.day_db) || 60;
        typeGroups[type].nightSum += Number(r.night_db) || 50;
        typeGroups[type].count += 1;
      });
      return Object.entries(typeGroups).map(([type, stats]) => ({
        name: type,
        Day_dB: Math.round((stats.daySum / stats.count) * 10) / 10,
        Night_dB: Math.round((stats.nightSum / stats.count) * 10) / 10
      }));
    }
    return [
      { name: 'Industrial', Day_dB: 71.4, Night_dB: 64.2 },
      { name: 'Commercial', Day_dB: 66.8, Night_dB: 58.1 },
      { name: 'Residential', Day_dB: 56.2, Night_dB: 47.9 },
      { name: 'Silence Zone', Day_dB: 49.8, Night_dB: 41.3 }
    ];
  }, [summary, records]);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header-text">
          <h1>Noise Pollution Monitoring</h1>
          <p>
            Continuous sound pressure levels, acoustic exposure metrics, and CPCB Noise Pollution (Regulation & Control) Rules compliance.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="filter-group">
          <Filter size={16} style={{ color: 'var(--text-muted)' }} />
          <span className="filter-label">Zone / Type:</span>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="form-select"
          >
            <option value="">All Acoustic Zones</option>
            {LOCATION_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
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

      {loading && <LoadingSpinner message="Polling ambient decibel sensors and acoustic monitors..." />}

      {!loading && error && (
        <ErrorState message={error} retry={fetchData} />
      )}

      {!loading && !error && records.length === 0 && !summary && (
        <EmptyState
          message="No noise telemetry records detected for selected location filter."
          suggestion="Select an urban center or enable demo mode."
        />
      )}

      {!loading && !error && (
        <>
          {/* 3 Stat Cards */}
          <div className="grid-3">
            <StatCard
              title="Average Day Sound Level"
              value={summary?.levels?.length ? (summary.levels.reduce((sum, level) => sum + level.avg_day_db, 0) / summary.levels.length).toFixed(1) : '—'}
              unit="dB(A)"
              subtitle="CPCB Day Period: 06:00 – 22:00"
              icon={Volume2}
              color="#ea580c"
            />

            <StatCard
              title="Average Night Sound Level"
              value={summary?.levels?.length ? (summary.levels.reduce((sum, level) => sum + level.avg_night_db, 0) / summary.levels.length).toFixed(1) : '—'}
              unit="dB(A)"
              subtitle="CPCB Night Period: 22:00 – 06:00"
              icon={Moon}
              color="#3b82f6"
            />

            <StatCard
              title="Statutory Limit Exceedances"
              value={summary?.exceedances_count ?? records.filter(r => checkExceedance(r.location_type || r.zone, r.day_db).exceeds).length}
              unit="Sensors"
              subtitle="Violating maximum decibel thresholds"
              icon={AlertTriangle}
              color="#ef4444"
            />
          </div>

          {/* Chart */}
          <EcoChart
            type="bar"
            data={dayNightChartData}
            xKey="name"
            keys={['Day_dB', 'Night_dB']}
            colors={['#f59e0b', '#3b82f6']}
            title="Acoustic Levels by Zone Type vs CPCB Ambient Standards"
            unit="dB(A)"
            height={340}
          />

          {/* Map */}
          <IndiaMap
            markers={mapMarkers}
            center={mapCenter}
            zoom={mapZoom}
            height={400}
            title={`Acoustic Monitoring Stations & Exceedance Status — ${location.city || location.state || 'India'}`}
          />

          {/* Table */}
          <div className="data-card">
            <div className="data-card-header">
              <h3 className="data-card-title">Acoustic Station Measurement Registry</h3>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Showing {records.length} records
              </span>
            </div>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Station Location</th>
                    <th>Zone Classification</th>
                    <th>Day Level (dB)</th>
                    <th>Night Level (dB)</th>
                    <th>CPCB Day Limit</th>
                    <th>Statutory Compliance</th>
                  </tr>
                </thead>
                <tbody>
                  {records.slice(0, 25).map((r, i) => {
                    const evalObj = checkExceedance(r.location_type || r.zone, r.day_db);
                    return (
                      <tr key={r.id || `np-${i}`}>
                        <td style={{ fontWeight: 600 }}>{r.station_name || r.location || `Sensor Station ${i + 1}`}</td>
                        <td>
                          <span className="badge badge-gray">{r.location_type || r.zone || 'Commercial'}</span>
                        </td>
                        <td style={{ fontWeight: 600 }}>{r.day_db} dB(A)</td>
                        <td>{r.night_db} dB(A)</td>
                        <td style={{ color: 'var(--text-muted)' }}>{evalObj.limit} dB(A)</td>
                        <td>
                          <span className={`badge ${evalObj.badge}`}>
                            {evalObj.label}
                          </span>
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
              Data Source: EcoVision Acoustic Intelligence (benchmarked against Central Pollution Control Board Ambient Air Quality Standards in respect of Noise Rules 2000).
            </span>
          </div>
        </>
      )}
    </div>
  );
}
