import { api } from '../api/client';

export type LoginRequest = {
  username: string;
  password: string;
};

export type RegisterRequest = {
  username: string;
  email: string;
  password: string;
};

export type AuthResponse = {
  access: string;
  refresh: string;
};

export const authService = {
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await api.post('/accounts/login/', data);
    return response.data;
  },

  async register(data: RegisterRequest): Promise<void> {
    await api.post('/accounts/register/', data);
  },
};