import { api } from './api';

export function getOverview({ state, city, demo } = {}) {
  const params = {};
  if (state) params.state = state;
  if (city) params.city = city;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/overview', { params });
}
