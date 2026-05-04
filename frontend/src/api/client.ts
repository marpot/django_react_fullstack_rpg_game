import axios from "axios";
import { config } from "../config/appConfig";

export const api = axios.create({
  baseURL: `${config.API_URL}/api`,
  withCredentials: true
});

api.interceptors.request.use((request) => {
  const token = localStorage.getItem("access_token");

  if (token) {
      request.headers.Authorization = `Bearer ${token}`;
    }
  
  return request;
});