import { api } from './api';

export function getWasteManagement({ state, city, demo, skip = 0, limit = 50 } = {}) {
  const params = { skip, limit };
  if (state) params.state = state;
  if (city) params.city = city;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/waste', { params });
}

export function getWasteSummary({ state, demo } = {}) {
  const params = {};
  if (state) params.state = state;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/waste/summary', { params });
}
