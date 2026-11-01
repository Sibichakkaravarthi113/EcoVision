import { api } from './api';

export function getNoisePollution({ state, city, locationType, demo, skip = 0, limit = 50 } = {}) {
  const params = { skip, limit };
  if (state) params.state = state;
  if (city) params.city = city;
  if (locationType) params.location_type = locationType;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/noise', { params });
}

export function getNoiseSummary({ state, demo } = {}) {
  const params = {};
  if (state) params.state = state;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/noise/summary', { params });
}
