import { api } from './api';

export function getAirQuality({ state, city, pollutant, demo, skip = 0, limit = 50 } = {}) {
  const params = { skip, limit };
  if (state) params.state = state;
  if (city) params.city = city;
  if (pollutant) params.pollutant = pollutant;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/air-quality', { params });
}

export function getPollutants() {
  return api.get('/api/air-quality/pollutants');
}

export function getAirQualityStates() {
  return api.get('/api/air-quality/states');
}

export function getAirQualitySummary({ state, city, demo } = {}) {
  const params = {};
  if (state) params.state = state;
  if (city) params.city = city;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/air-quality/summary', { params });
}
