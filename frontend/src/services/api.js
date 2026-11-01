
import axios from 'axios';

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    let message = 'An unexpected network error occurred';

    if (error.response) {
      message =
        error.response.data?.detail ||
        error.response.data?.message ||
        `Error ${error.response.status}: ${error.response.statusText}`;
    } else if (error.request) {
      message = 'EcoVision backend server is not reachable.';
    } else {
      message = error.message;
    }

    const err = new Error(message);
    err.original = error;
    return Promise.reject(err);
  }
);
