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
  baseURL: `/api`,
  withCredentials: true,
});

// REQUEST INTERCEPTOR
api.interceptors.request.use((request) => {
  const token = localStorage.getItem("access_token");

  console.log("REQUEST:", request.url);
  console.log("TOKEN:", token);

  const isPublic =
    PUBLIC_ENDPOINTS.some((url) => request.url?.includes(url)) ||
    LEGACY_PUBLIC_ENDPOINTS.some((url) => request.url?.includes(url));

  if (token && !isPublic) {
    request.headers?.set?.("Authorization", `Bearer ${token}`);
  }

  return request;
});

// RESPONSE INTERCEPTOR
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const code = error.response?.data?.code;

    if (code === "token_not_valid") {
      console.warn("[AUTH] Token invalid - keeping storage, letting requests handle auth");
    }

    return Promise.reject(error);
  }
);