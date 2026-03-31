fetch(`${API_BASE_URL}/api/employee`)
import axios from "axios";

// 🔥 CHANGE THIS ONLY
const API_BASE_URL = "https://worksheet3-liart.vercel.app";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// interceptor (leave as it is)
api.interceptors.request.use(
  (config) => {
    const savedUser = localStorage.getItem("user_v2");
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

// sample API
export const getData = async () => {
  const res = await api.get("/");
  return res.data;
};

export default api;
