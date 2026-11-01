import { api } from './api';

export function getGreenCoverage({ state, district, demo, skip = 0, limit = 50 } = {}) {
  const params = { skip, limit };
  if (state) params.state = state;
  if (district) params.district = district;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/green-coverage', { params });
}

export function getGreenCoverageSummary({ state, demo } = {}) {
  const params = {};
  if (state) params.state = state;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/green-coverage/summary', { params });
}
