import axios from 'axios';

// In production, we always use the relative /api which Nginx proxies to the backend
const API_BASE_URL = '/api/';

console.log(`[API] Initialized with Base URL: ${API_BASE_URL}`);

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000, // Increased timeout for RDS latency
});

// Add request interceptor
api.interceptors.request.use(
    (config) => {
        const savedUser = localStorage.getItem('user_v2');
        if (savedUser) {
            const { token } = JSON.parse(savedUser);
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default api;
