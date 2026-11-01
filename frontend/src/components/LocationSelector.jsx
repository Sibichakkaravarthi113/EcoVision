import React, { useMemo } from 'react';
import { MapPin } from 'lucide-react';
import { useLocationCtx } from '../context/LocationContext';
import { INDIA_LOCATIONS, getDistricts, getCities } from '../data/indiaLocations';

export default function LocationSelector({ compact = false }) {
  const { location, setLocation } = useLocationCtx();

  const districts = useMemo(() => {
    return getDistricts(location.state);
  }, [location.state]);

  const cities = useMemo(() => {
    return getCities(location.state, location.district);
  }, [location.state, location.district]);

  const handleStateChange = (e) => {
    const nextState = e.target.value;
    setLocation({ state: nextState });
  };

  const handleDistrictChange = (e) => {
    const nextDistrict = e.target.value;
    setLocation({ district: nextDistrict });
  };

  const handleCityChange = (e) => {
    const nextCity = e.target.value;
    setLocation({ city: nextCity });
  };

  return (
    <div className={compact ? 'location-selector' : 'filter-bar'} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <MapPin size={compact ? 16 : 18} style={{ color: 'var(--primary-light)', flexShrink: 0 }} />

      <select
        value={location.state || ''}
        onChange={handleStateChange}
        className={compact ? '' : 'form-select'}
        title="Select State"
        style={compact ? {} : { minWidth: '150px' }}
      >
        <option value="">All States</option>
        {INDIA_LOCATIONS.states.map((s) => (
          <option key={s.name} value={s.name}>
            {s.name}
          </option>
        ))}
      </select>

      <span style={{ color: 'var(--border-color)', fontWeight: 300 }}>/</span>

      <select
        value={location.district || ''}
        onChange={handleDistrictChange}
        disabled={!location.state}
        className={compact ? '' : 'form-select'}
        title="Select District"
        style={compact ? {} : { minWidth: '140px' }}
      >
        <option value="">All Districts</option>
        {districts.map((d) => (
          <option key={d.name} value={d.name}>
            {d.name}
          </option>
        ))}
      </select>

      <span style={{ color: 'var(--border-color)', fontWeight: 300 }}>/</span>

      <select
        value={location.city || ''}
        onChange={handleCityChange}
        disabled={!location.district}
        className={compact ? '' : 'form-select'}
        title="Select City"
        style={compact ? {} : { minWidth: '130px' }}
      >
        <option value="">All Cities</option>
        {cities.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>
    </div>
  );
}
