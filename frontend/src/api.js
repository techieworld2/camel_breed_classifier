import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  signup: (username, email, password) =>
    apiClient.post('/auth/signup', { username, email, password }),
  login: (username, password) =>
    apiClient.post('/auth/login', { username, password }),
  getCurrentUser: () =>
    apiClient.get('/auth/me'),
  logout: () =>
    apiClient.post('/auth/logout'),
};

export const predictionAPI = {
  classify: (formData) =>
    apiClient.post('/predict/classify', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getHistory: (skip = 0, limit = 10) =>
    apiClient.get('/predict/history', { params: { skip, limit } }),
  getPrediction: (id) =>
    apiClient.get(`/predict/${id}`),
  deletePrediction: (id) =>
    apiClient.delete(`/predict/${id}`),
};

export const featureAPI = {
  getBreedFacts: (breedName) =>
    apiClient.post(`/features/facts?breed_name=${encodeURIComponent(breedName)}`),
};

export default apiClient;
