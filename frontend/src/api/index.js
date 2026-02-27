// Centralized API client using Axios

import axios from 'axios';

// local testing URL: http://127.0.0.1:5000/
// production URL: http://d0018e-demo-env.eba-w8mzvug5.eu-north-1.elasticbeanstalk.com

// Single axios instance with relative base URL
const api = axios.create({
  baseURL: 'http://127.0.0.1:5000/',           // Base URL
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Show error details in console for easier debugging
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default api;