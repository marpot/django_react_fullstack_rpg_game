import axios from "axios";

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

  const isPublic =
    PUBLIC_ENDPOINTS.some((url) => request.url?.includes(url)) ||
    LEGACY_PUBLIC_ENDPOINTS.some((url) => request.url?.includes(url));

  // DEBUG ONLY (bez spamowania tokenem)
  if (process.env.NODE_ENV === "development") {
    if (!request.url?.includes("/accounts/me/")) {
      console.log("[API REQUEST]", request.method?.toUpperCase(), request.url);
    }
  }

  if (token && !isPublic) {
    request.headers.set?.("Authorization", `Bearer ${token}`);
  }

  return request;
});

// RESPONSE INTERCEPTOR
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const code = error.response?.data?.code;

    if (code === "token_not_valid") {
      console.warn("[AUTH] token invalid");
    }

    return Promise.reject(error);
  }
);