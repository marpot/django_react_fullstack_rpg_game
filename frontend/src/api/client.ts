import axios from "axios";
import { config } from "../config/appConfig";

const PUBLIC_ENDPOINTS = [
  "/auth/register",
  "/auth/login",
  "/auth/refresh",
];

const LEGACY_PUBLIC_ENDPOINTS = [
  "/accounts/login/",
  "/accounts/register/",
  "/accounts/token/refresh/",
];

export const api = axios.create({
  baseURL: `${config.API_URL}/api`,
  withCredentials: true,
});

// REQUEST INTERCEPTOR
api.interceptors.request.use((request) => {
  const token = localStorage.getItem("access_token");

  const isPublic =
    PUBLIC_ENDPOINTS.some((url) => request.url?.includes(url)) ||
    LEGACY_PUBLIC_ENDPOINTS.some((url) => request.url?.includes(url));

  if (token && !isPublic) {
    request.headers.Authorization = `Bearer ${token}`;
  }

  return request;
});

// RESPONSE INTERCEPTOR
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const code = error.response?.data?.code;

    if (code === "token_not_valid") {
      console.warn("Token invalid => clearing storage");

      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }

    return Promise.reject(error);
  }
);