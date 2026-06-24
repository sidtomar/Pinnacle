import axios from 'axios';
import Constants from 'expo-constants';

// Change this to your machine's LAN IP when testing on a physical device.
// localhost won't work on a phone — use the IP shown when you run `expo start`.
const BASE_URL = Constants.expoConfig?.extra?.apiUrl || 'http://localhost:8010';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

export const getContent = () => api.get('/content');
export const getDoctors = () => api.get('/doctors');
export const getOccasions = () => api.get('/occasions');
export const logShare = (contentId, doctorId, channel) =>
  api.post('/share/log', { content_id: contentId, doctor_id: doctorId, channel });

export default api;
