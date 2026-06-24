import axios from 'axios';

// Expo web doesn't always read app.json extra config — hardcode localhost for web dev
const BASE_URL = typeof window !== 'undefined'
  ? 'http://localhost:8010'          // browser (Expo web)
  : 'http://localhost:8010';         // native (update to LAN IP for physical device)

console.log('[API] Base URL:', BASE_URL);

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// Log every request and error so we can debug in browser console
api.interceptors.request.use(req => { console.log('[API] -->', req.method?.toUpperCase(), req.url); return req; });
api.interceptors.response.use(
  res => { console.log('[API] <--', res.status, res.config.url); return res; },
  err => { console.error('[API] ERR', err.config?.url, err.message); return Promise.reject(err); }
);

export const getContent  = () => api.get('/content');
export const getDoctors  = () => api.get('/doctors');
export const getOccasions = () => api.get('/occasions');
export const logShare    = (contentId, doctorId, channel) =>
  api.post('/share/log', { content_id: contentId, doctor_id: doctorId, channel });

export default api;
