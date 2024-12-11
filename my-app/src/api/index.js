// src/api/index.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/', // Replace with your backend URL
});

function waitForToken(timeout = 5000) {
  return new Promise((resolve, reject) => {
    let elapsed = 0;
    const interval = setInterval(() => {
      const token = localStorage.getItem('access_token');

      if (token) {
        clearInterval(interval);
        resolve(token);
      }
      elapsed += 50;
      if (elapsed >= timeout) {
        clearInterval(interval);
        console.error('api/index.js: Token not found within timeout.');
        reject(new Error('Token not found within timeout.'));
      }
    }, 50);
  });
}

api.interceptors.request.use(
  async (config) => {
    // Excluded endpoints
    const excludedEndpoints = ['/token', '/auth/register'];
    if (excludedEndpoints.some((url) => config.url.startsWith(url))) {
      return config;
    }

    let token = localStorage.getItem('access_token');

    if (!token) {
      console.warn('api/index.js: No token in localStorage. Waiting for token...');
      try {
        token = await waitForToken(); // Wait for token to appear
      } catch (error) {
        console.error('api/index.js: Failed to retrieve token:', error);
        return config; // Proceed without token if not found
      }
    }

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      console.warn('api/index.js: No token available to attach.');
    }
    return config;
  },
  (error) => {
    console.error('api/index.js: Request interceptor error:', error);
    return Promise.reject(error);
  }
);


// Handle responses and global errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Optionally, handle unauthorized errors globally
      console.warn('Received 401 Unauthorized response.');
      // Uncomment the lines below to clear storage and redirect
      // localStorage.clear();
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
