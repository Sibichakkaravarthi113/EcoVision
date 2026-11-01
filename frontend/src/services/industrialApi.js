import { api } from './api';

export function getIndustrialActivity({ state, district, industryType, demo, skip = 0, limit = 50 } = {}) {
  const params = { skip, limit };
  if (state) params.state = state;
  if (district) params.district = district;
  if (industryType) params.industry_type = industryType;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/industrial', { params });
}

export function getIndustrialSummary({ state, demo } = {}) {
  const params = {};
  if (state) params.state = state;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/industrial/summary', { params });
}
