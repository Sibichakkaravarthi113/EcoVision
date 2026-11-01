import { api } from './api';

export function sendMessage({ message, location, demo_mode = false, history = [] } = {}) {
  const payload = {
    message,
    demo_mode: Boolean(demo_mode),
    history: Array.isArray(history) ? history : []
  };
  if (location) {
    payload.location = location;
  }
  return api.post('/api/chat', payload);
}
