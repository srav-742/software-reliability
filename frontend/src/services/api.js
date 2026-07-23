import axios from 'axios';

const getApiBaseUrl = () => {
  let envUrl = import.meta.env.VITE_API_URL;
  if (!envUrl) return '/api/v1';
  
  envUrl = envUrl.trim().replace(/['"]/g, '').replace(/\/+$/, '');
  if (envUrl.startsWith('http') && !envUrl.endsWith('/api/v1')) {
    envUrl = `${envUrl}/api/v1`;
  }
  return envUrl;
};

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Interceptor to append Authorization header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

// Interceptor to handle auth errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authApi = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  getProfile: () => api.get('/auth/profile'),
};

// Projects endpoints
export const projectApi = {
  getAll: (skip = 0, limit = 100) => api.get(`/projects/?skip=${skip}&limit=${limit}`),
  getById: (id) => api.get(`/projects/${id}`),
  create: (formData) => api.post('/projects/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  update: (id, formData) => api.put(`/projects/${id}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  delete: (id) => api.delete(`/projects/${id}`),
};

// Feature Extraction & Analysis endpoints
export const analysisApi = {
  analyzeProject: (id) => api.post(`/projects/${id}/analyze`),
  getMetrics: (id) => api.get(`/projects/${id}/metrics`),
};

// Prediction endpoints
export const predictApi = {
  predictProject: (id) => api.post(`/projects/${id}/predict`),
  getHistoryByProject: (id) => api.get(`/projects/${id}/predictions`),
  getAllHistory: () => api.get('/history'),
};

// Explainability endpoints
export const explainApi = {
  getExplanation: (id) => api.get(`/projects/${id}/explain`),
};

// Model Registry endpoints
export const modelApi = {
  getModels: () => api.get('/models'),
  getActiveModel: () => api.get('/models/active'),
  activateModel: (modelId) => api.put(`/models/${modelId}/activate`),
};

// Training endpoints
export const trainApi = {
  trainModels: (data = {}) => api.post('/train', data),
  getHistory: () => api.get('/train/history'),
};

// Health endpoint
export const healthApi = {
  check: () => api.get('/health'),
};

// API Key endpoints
export const apiKeyApi = {
  getAll: () => api.get('/auth/api-keys/'),
  create: (name) => api.post('/auth/api-keys/', { name }),
  revoke: (id) => api.delete(`/auth/api-keys/${id}`),
};

// CI/CD Scan endpoints
export const cicdApi = {
  getScans: (projectId = null) => api.get(`/cicd/scans${projectId ? `?project_id=${projectId}` : ''}`),
  getScanById: (id) => api.get(`/cicd/scans/${id}`),
};

// API Key Scanner endpoints
export const scanApi = {
  scanKeys: (projectId) => api.post(`/projects/${projectId}/scan-keys`),
  getResults: (projectId) => api.get(`/projects/${projectId}/scan-keys`),
  getHistory: (projectId) => api.get(`/projects/${projectId}/scan-keys/history`),
};

export default api;
