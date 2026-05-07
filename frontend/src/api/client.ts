import axios from "axios";
import { config } from "../config/appConfig";

export const api = axios.create({
  baseURL: `${config.API_URL}/api`,
  withCredentials: true,
});

const publicEndpoints = [
  "/accounts/login/",
  "/accounts/register/",
  "/accounts/token/refresh/",
];

api.interceptors.request.use((request) => {
  const token = localStorage.getItem("access_token");
  const isPublicEndpoint = publicEndpoints.some((endpoint) =>
    request.url?.includes(endpoint),
  );

  if (token && !isPublicEndpoint) {
    request.headers.Authorization = `Bearer ${token}`;
  }

  return request;
});
