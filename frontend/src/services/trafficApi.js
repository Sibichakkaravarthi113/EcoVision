import { api } from './api';

export function getTrafficCongestion({ state, city, level, demo, skip = 0, limit = 50 } = {}) {
  const params = { skip, limit };
  if (state) params.state = state;
  if (city) params.city = city;
  if (level) params.congestion_level = level;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/traffic', { params });
}

export function getTrafficSummary({ state, city, demo } = {}) {
  const params = {};
  if (state) params.state = state;
  if (city) params.city = city;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/traffic/summary', { params });
}
