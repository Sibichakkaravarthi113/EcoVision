import { api } from './api';

export function getWaterQuality({ state, district, station, parameter, demo, skip = 0, limit = 50 } = {}) {
  const params = { skip, limit };
  if (state) params.state = state;
  if (district) params.district = district;
  if (station) params.station = station;
  if (parameter) params.parameter = parameter;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/water-quality', { params });
}

export function getWaterParameters() {
  return api.get('/api/water-quality/parameters');
}

export function getWaterSummary({ state, demo } = {}) {
  const params = {};
  if (state) params.state = state;
  if (demo !== undefined) params.demo = demo;
  return api.get('/api/water-quality/summary', { params });
}
