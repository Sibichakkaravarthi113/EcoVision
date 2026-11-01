import { api } from './api';

export function getClimateConditions({ state, city, demo, skip = 0, limit = 50 } = {}) {
  const params = { skip, limit };
  if (state) params.state = state;
  if (city) params.city = city;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/climate', { params });
}

export function getClimateSummary({ state, city, demo } = {}) {
  const params = {};
  if (state) params.state = state;
  if (city) params.city = city;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/climate/summary', { params });
}

export function getClimateForecast({ state, city, lat, lon } = {}) {
  const params = {};
  if (state) params.state = state;
  if (city) params.city = city;
  if (lat !== undefined) params.lat = lat;
  if (lon !== undefined) params.lon = lon;
  return api.get('/api/climate/forecast', { params });
}
