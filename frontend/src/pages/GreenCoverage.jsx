import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Trees, Compass, MapPin, Filter } from 'lucide-react';
import { useDemoMode } from '../context/DemoModeContext';
import { useLocationCtx } from '../context/LocationContext';
import { getGreenCoverage, getGreenCoverageSummary } from '../services/greenCoverageApi';
import { resolveCoordinates, getDistricts } from '../data/indiaLocations';
import StatCard from '../components/StatCard';
import IndiaMap from '../components/IndiaMap';
import EcoChart from '../components/EcoChart';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorState from '../components/ErrorState';
import EmptyState from '../components/EmptyState';

export default function GreenCoverage() {
  const { demoMode } = useDemoMode();
  const { location, setLocation } = useLocationCtx();

  const [districtsData, setDistrictsData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const availableDistricts = useMemo(() => {
    return getDistricts(location.state);
  }, [location.state]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [dataRes, summaryRes] = await Promise.all([
        getGreenCoverage({
          state: location.state || undefined,
          district: location.district || undefined,
          demo: demoMode ? true : undefined,
          limit: 100
        }),
        getGreenCoverageSummary({
          state: location.state || undefined,
          demo: demoMode ? true : undefined
        })
      ]);

      setDistrictsData(Array.isArray(dataRes) ? dataRes : (dataRes?.items || []));
      setSummary(summaryRes);
    } catch (err) {
      setError(err.message || 'Failed to fetch forest coverage records');
    } finally {
      setLoading(false);
    }
  }, [location.state, location.district, demoMode]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const mapCenter = useMemo(() => {
    return resolveCoordinates(location.city, location.state);
  }, [location.city, location.state]);

  const mapZoom = useMemo(() => {
    if (location.district) return 9;
    if (location.state) return 7;
    return 5;
  }, [location.district, location.state]);

  // District markers sized by coverage %
  const mapMarkers = useMemo(() => {
    if (districtsData.length > 0) {
      return districtsData
        .filter((d) => d.latitude && d.longitude)
        .map((d) => {
          const pct = Number(d.forest_cover_percent) || 0;
          return {
            lat: Number(d.latitude),
            lng: Number(d.longitude),
            label: `${d.district_name || 'District'} (${pct}% Forest)`,
            title: `${d.district_name || 'District'} Forest Division`,
            value: pct,
            unit: '% cover',
            radius: Math.max(6, Math.min(22, Math.round(pct / 3))),
            status: pct > 33 ? 'Above National Target' : 'Below 33% Target',
            color: pct > 33 ? '#059669' : pct > 15 ? '#10b981' : '#f59e0b'
          };
        });
    }

    if (summary) {
      const base = resolveCoordinates(location.city, location.state);
      const pct = Number(summary.avg_forest_cover_percent) || 0;
      return [
        {
          lat: base[0],
          lng: base[1],
          label: `${location.state || 'State'} Regional Canopy`,
          title: 'Forest Canopy Observation Division',
          value: pct,
          unit: '% Forest Cover',
          radius: 14,
          status: 'Protected Reserve',
          color: '#10b981'
        }
      ];
    }
    return [];
  }, [districtsData, summary, location.city, location.state]);

  // Bar chart: Forest cover % by district
  const districtBarChartData = useMemo(() => {
    if (districtsData.length > 0) {
      return districtsData.slice(0, 10).map((d) => ({
        name: d.district_name ? (d.district_name.length > 11 ? d.district_name.substring(0, 11) + '..' : d.district_name) : 'District',
        percentage: Number(d.forest_cover_percent) || 0
      }));
    }
    return [];
  }, [districtsData]);

  // Breakdown chart: VDF vs MDF vs Open Forest
  const forestTypeChartData = useMemo(() => {
    if (districtsData.length > 0) {
      let vdfSum = 0;
      let mdfSum = 0;
      let openSum = 0;
      districtsData.forEach((d) => {
        vdfSum += Number(d.very_dense_forest) || 0;
        mdfSum += Number(d.moderate_dense_forest) || 0;
        openSum += Number(d.open_forest) || 0;
      });
      return [
        { name: 'Very Dense (VDF)', area: Math.round(vdfSum) },
        { name: 'Mod. Dense (MDF)', area: Math.round(mdfSum) },
        { name: 'Open Forest (OF)', area: Math.round(openSum) }
      ];
    }
    return [];
  }, [summary, districtsData]);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header-text">
          <h1>Forest & Green Coverage</h1>
          <p>
            Canopy density, tree cover indices, and ecological land classification based on satellite observation.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="filter-group">
          <Filter size={16} style={{ color: 'var(--text-muted)' }} />
          <span className="filter-label">Filter District:</span>
          <select
            value={location.district || ''}
            onChange={(e) => setLocation({ district: e.target.value })}
            className="form-select"
            disabled={!location.state}
          >
            <option value="">All State Districts</option>
            {availableDistricts.map((d) => (
              <option key={d.name} value={d.name}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading && <LoadingSpinner message="Calculating satellite green canopy densities..." />}

      {!loading && error && (
        <ErrorState message={error} retry={fetchData} />
      )}

      {!loading && !error && districtsData.length === 0 && !summary && (
        <EmptyState
          message="No forest inventory data located for this geographical scope."
          suggestion="Select a valid state or toggle demo mode."
        />
      )}

      {!loading && !error && (
        <>
          {/* 3 Stat Cards */}
          <div className="grid-3">
            <StatCard
              title="Total Recorded Forest Area"
              value={summary?.total_forest_area_sqkm ?? 0}
              unit="sq km"
              subtitle="Recorded Forest Area (RFA)"
              icon={Trees}
              color="#059669"
            />

            <StatCard
              title="Forest Cover Percentage"
              value={summary?.avg_forest_cover_percent ?? 0}
              unit="%"
              subtitle="National Forest Policy Target: 33%"
              icon={Compass}
              color="#10b981"
            />

            <StatCard
              title="Very Dense Forest (VDF)"
              value={summary?.very_dense_forest_sqkm ?? districtsData.reduce((acc, d) => acc + (Number(d.very_dense_forest) || 0), 0)}
              unit="sq km"
              subtitle="Canopy Density > 70%"
              icon={MapPin}
              color="#15803d"
            />
          </div>

          {/* Charts Row */}
          <div className="grid-2">
            <EcoChart
              type="bar"
              data={districtBarChartData}
              xKey="name"
              yKey="percentage"
              title="Forest Cover Percentage by District"
              unit="%"
              color="#16a34a"
            />

            <EcoChart
              type="bar"
              data={forestTypeChartData}
              xKey="name"
              yKey="area"
              title="Canopy Density Classification"
              unit="sq km"
              color="#059669"
            />
          </div>

          {/* Map */}
          <IndiaMap
            markers={mapMarkers}
            center={mapCenter}
            zoom={mapZoom}
            height={400}
            title={`District Forest Canopy Distribution — ${location.district || location.state || 'India'}`}
          />

          {/* District Forest Table */}
          <div className="data-card">
            <div className="data-card-header">
              <h3 className="data-card-title">District Forest Inventory & Density Registry</h3>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Showing {districtsData.length} districts
              </span>
            </div>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>District</th>
                    <th>Geographic Area</th>
                    <th>Total Forest Area</th>
                    <th>Coverage %</th>
                    <th>Very Dense (VDF)</th>
                    <th>Mod. Dense (MDF)</th>
                    <th>Open Forest (OF)</th>
                  </tr>
                </thead>
                <tbody>
                  {districtsData.slice(0, 25).map((d, i) => {
                    const cov = Number(d.coverage_percentage || d.forest_percentage || 0);
                    return (
                      <tr key={d.id || `fc-${i}`}>
                        <td style={{ fontWeight: 600 }}>{d.district || `District ${i + 1}`}</td>
                        <td>{d.geographic_area ? `${d.geographic_area} sq km` : '—'}</td>
                        <td style={{ fontWeight: 600 }}>{d.forest_area ? `${d.forest_area} sq km` : '—'}</td>
                        <td>
                          <span className={`badge ${cov >= 33 ? 'badge-green' : cov >= 15 ? 'badge-yellow' : 'badge-orange'}`}>
                            {cov}%
                          </span>
                        </td>
                        <td>{d.vdf_area || d.very_dense_forest || '—'} sq km</td>
                        <td>{d.mdf_area || d.moderately_dense_forest || '—'} sq km</td>
                        <td>{d.open_forest_area || d.open_forest || '—'} sq km</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="data-source-note">
            <span>
              Data Source: Forest Survey of India (FSI) Biennial India State of Forest Report (ISFR) 2023 / EcoVision Earth Observation Engine.
            </span>
          </div>
        </>
      )}
    </div>
  );
}
