import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Trash2, Recycle, Truck, Filter } from 'lucide-react';
import { useDemoMode } from '../context/DemoModeContext';
import { useLocationCtx } from '../context/LocationContext';
import { getWasteManagement, getWasteSummary } from '../services/wasteApi';
import { resolveCoordinates, getCities } from '../data/indiaLocations';
import StatCard from '../components/StatCard';
import IndiaMap from '../components/IndiaMap';
import EcoChart from '../components/EcoChart';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorState from '../components/ErrorState';
import EmptyState from '../components/EmptyState';

export default function WasteManagement() {
  const { demoMode } = useDemoMode();
  const { location, setLocation } = useLocationCtx();

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
        getWasteManagement({
          state: location.state || undefined,
          city: location.city || undefined,
          demo: demoMode ? true : undefined,
          limit: 100
        }),
        getWasteSummary({
          state: location.state || undefined,
          demo: demoMode ? true : undefined
        })
      ]);

      setRecords(Array.isArray(resData) ? resData : (resData?.items || []));
      setSummary(resSummary);
    } catch (err) {
      setError(err.message || 'Failed to fetch waste management metrics');
    } finally {
      setLoading(false);
    }
  }, [location.state, location.city, demoMode]);

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

  const mapMarkers = useMemo(() => {
    if (records.length > 0) {
      return records
        .filter((r) => r.latitude && r.longitude)
        .map((r) => {
          const recRate = Number(r.recycling_rate) || 50;
          return {
            lat: Number(r.latitude),
            lng: Number(r.longitude),
            label: `${r.city || 'City'} (${recRate}% Recycled)`,
            title: `${r.city} Municipal Waste Facility`,
            value: r.generated_tonnes_day || 0,
            unit: 'TPD Generated',
            status: recRate >= 65 ? 'High Efficiency' : 'Standard Processing',
            color: recRate >= 65 ? '#10b981' : '#f59e0b'
          };
        });
    }

    if (summary) {
      const base = resolveCoordinates(location.city, location.state);
      return [
        {
          lat: base[0],
          lng: base[1],
          label: `${location.city || location.state || 'Municipal'} Waste Center`,
          title: 'Integrated Waste Management Facility',
          value: summary.total_generated_tonnes_day || 0,
          unit: 'TPD Generated',
          status: 'Operational Processing',
          color: '#10b981'
        }
      ];
    }
    return [];
  }, [records, summary, location.city, location.state]);

  // Bar chart: Generated vs Collected vs Processed
  const wasteComparisonChartData = useMemo(() => {
    if (records.length > 0) {
      return records.slice(0, 8).map((r) => ({
        name: r.city ? (r.city.length > 10 ? r.city.substring(0, 10) + '..' : r.city) : 'City',
        Generated: Number(r.generated_tonnes_day) || 0,
        Collected: Number(r.collected_tonnes_day) || 0,
        Processed: Number(r.processed_tonnes_day) || 0
      }));
    }
    return [];
  }, [records]);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header-text">
          <h1>Waste Management</h1>
          <p>
            Solid Waste Management (SWM) statistics, processing capacities, and municipal recovery efficiencies.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="filter-group">
          <Filter size={16} style={{ color: 'var(--text-muted)' }} />
          <span className="filter-label">Filter City:</span>
          <select
            value={location.city || ''}
            onChange={(e) => setLocation({ city: e.target.value })}
            className="form-select"
            disabled={!location.state}
          >
            <option value="">All State Cities</option>
            {availableCities.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading && <LoadingSpinner message="Aggregating municipal solid waste statistics..." />}

      {!loading && error && (
        <ErrorState message={error} retry={fetchData} />
      )}

      {!loading && !error && records.length === 0 && !summary && (
        <EmptyState
          message="No municipal waste management data found for selected location."
          suggestion="Select a larger metropolitan area or activate demo mode."
        />
      )}

      {!loading && !error && (
        <>
          {/* 3 Stat Cards */}
          <div className="grid-3">
            <StatCard
              title="Daily Waste Generated"
              value={summary?.total_generated_tonnes_day ?? records.reduce((acc, r) => acc + (Number(r.generated_tonnes_day) || 0), 0)}
              unit="TPD"
              subtitle="Tonnes Per Day (TPD)"
              icon={Trash2}
              color="#d97706"
            />

            <StatCard
              title="Collection Efficiency"
              value={summary?.collection_efficiency_percent ?? 0}
              unit="%"
              subtitle="Door-to-door segregated collection"
              icon={Truck}
              color="#0284c7"
            />

            <StatCard
              title="Recycling & Recovery Rate"
              value={summary?.avg_recycling_percent ?? 0}
              unit="%"
              subtitle="Material Recovery Facility (MRF) diversion"
              icon={Recycle}
              color="#10b981"
            />
          </div>

          {/* Chart */}
          <EcoChart
            type="bar"
            data={wasteComparisonChartData}
            xKey="name"
            keys={['Generated', 'Collected', 'Processed']}
            colors={['#f59e0b', '#3b82f6', '#10b981']}
            title="Municipal Waste Lifecycle: Generated vs Collected vs Processed"
            unit="TPD"
            height={340}
          />

          {/* Map */}
          <IndiaMap
            markers={mapMarkers}
            center={mapCenter}
            zoom={mapZoom}
            height={400}
            title={`Solid Waste Processing Facilities — ${location.city || location.state || 'India'}`}
          />

          {/* Table */}
          <div className="data-card">
            <div className="data-card-header">
              <h3 className="data-card-title">Municipal Solid Waste Performance Log</h3>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Showing {records.length} records
              </span>
            </div>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>City / Municipality</th>
                    <th>Waste Generated (TPD)</th>
                    <th>Waste Collected (TPD)</th>
                    <th>Waste Processed (TPD)</th>
                    <th>Recycling Rate</th>
                    <th>Audit Year</th>
                  </tr>
                </thead>
                <tbody>
                  {records.slice(0, 25).map((r, i) => {
                    const rec = Number(r.recycling_rate || 50);
                    return (
                      <tr key={r.id || `wm-${i}`}>
                        <td style={{ fontWeight: 600 }}>{r.city || `City ${i + 1}`}</td>
                        <td>{r.generated_tonnes_day ?? '—'} TPD</td>
                        <td>{r.waste_collected_tpd || r.collected_tpd || '—'} TPD</td>
                        <td style={{ fontWeight: 600 }}>{r.waste_processed_tpd || r.processed_tpd || '—'} TPD</td>
                        <td>
                          <span className={`badge ${rec >= 65 ? 'badge-green' : rec >= 45 ? 'badge-yellow' : 'badge-orange'}`}>
                            {rec}%
                          </span>
                        </td>
                        <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{r.year || '2024'}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="data-source-note">
            <span>
              Data Source: EcoVision Municipal Analytics (synthesized from Central Pollution Control Board Solid Waste Management Rules 2016 implementation reviews).
            </span>
          </div>
        </>
      )}
    </div>
  );
}
