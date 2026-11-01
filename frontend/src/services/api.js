import axios from 'axios';

const BASE_URL = import.meta.env?.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Response interceptor for consistent error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    let message = 'An unexpected network error occurred';
    if (error.response) {
      // Backend returned an error response
      message = error.response.data?.detail || error.response.data?.message || `Error ${error.response.status}: ${error.response.statusText}`;
    } else if (error.request) {
      // Request was made but no response received
      message = 'EcoVision backend server is not reachable. Please check if the FastAPI backend is running on port 8000.';
    } else {
      message = error.message;
    }
    const err = new Error(message);
    err.original = error;
    return Promise.reject(err);
  }
);
