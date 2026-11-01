import React, { createContext, useContext, useState, useEffect } from 'react';

const LocationContext = createContext();

const DEFAULT_LOCATION = {
  country: 'India',
  state: '',
  district: '',
  city: '',
  monitoringLocation: ''
};

export function LocationProvider({ children }) {
  const [location, setLocationState] = useState(() => {
    try {
      const saved = localStorage.getItem('ecovision_location');
      return saved ? JSON.parse(saved) : DEFAULT_LOCATION;
    } catch {
      return DEFAULT_LOCATION;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem('ecovision_location', JSON.stringify(location));
    } catch (e) {
      console.warn('Failed to persist location context:', e);
    }
  }, [location]);

  const setLocation = (updates) => {
    setLocationState(prev => {
      const next = { ...prev, ...updates };

      // When state changes to a new value, reset child levels
      if ('state' in updates && updates.state !== prev.state) {
        if (!('district' in updates)) next.district = '';
        if (!('city' in updates)) next.city = '';
        if (!('monitoringLocation' in updates)) next.monitoringLocation = '';
      }

      // When district changes to a new value, reset child levels
      if ('district' in updates && updates.district !== prev.district) {
        if (!('city' in updates)) next.city = '';
        if (!('monitoringLocation' in updates)) next.monitoringLocation = '';
      }

      return next;
    });
  };

  const clearLocation = () => {
    setLocationState(DEFAULT_LOCATION);
  };

  return (
    <LocationContext.Provider value={{ location, setLocation, clearLocation }}>
      {children}
    </LocationContext.Provider>
  );
}

export function useLocationCtx() {
  const context = useContext(LocationContext);
  if (!context) {
    throw new Error('useLocationCtx must be used within a LocationProvider');
  }
  return context;
}
