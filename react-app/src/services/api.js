import axios from 'axios';

// Dev: call localhost:8010 directly. Production (Railway): same origin, empty base = relative URLs.
const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8010' : '');

const client = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor for debugging
client.interceptors.request.use(config => {
  console.log(`[API] ${config.method.toUpperCase()} ${config.url}`);
  return config;
}, error => Promise.reject(error));

// Response interceptor for error handling
client.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      console.warn('Unauthorized access');
    }
    return Promise.reject(error);
  }
);

export const api = {
  // Content endpoints
  content: {
    list: () => client.get('/content'),
    get: (id) => client.get(`/content/${id}`),
    create: (data) => client.post('/content', data),
    update: (id, data) => client.put(`/content/${id}`, data),
    delete: (id) => client.delete(`/content/${id}`)
  },

  // Sharing/Analytics endpoints
  sharing: {
    logShare: (contentId, method) =>
      client.post(`/content/${contentId}/share`, { method }),
    getReport: () => client.get('/share-logs'),
    getBusinessReport: () => client.get('/report/download')
  },

  // Pipeline endpoints
  pipeline: {
    run: (input) => client.post('/pipeline/run', { input }),
    save: (output) => client.post('/pipeline/save', { output })
  },

  // Doctor endpoints
  doctors: {
    list: () => client.get('/doctors'),
    search: (query) => client.get('/doctors/search', { params: { q: query } })
  }
};

export default client;
