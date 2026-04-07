import axios from 'axios';

// ✅ YOUR SERVER IP + PORT
const API_BASE_URL = "/api";

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000,
});

// 🔐 Attach token
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
    (error) => Promise.reject(error)
);

export default api;
