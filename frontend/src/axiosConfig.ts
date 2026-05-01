import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8001/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// Endpointy publiczne (bez JWT)
const PUBLIC_ENDPOINTS = [
  "/accounts/register/",
  "/accounts/login/",
];

// INTERCEPTOR
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access");

    const url = config.url || "";

    const isPublic = PUBLIC_ENDPOINTS.some((endpoint) =>
      url.includes(endpoint)
    );

    // Dodaj token tylko do chronionych endpointów
    if (token && !isPublic) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;