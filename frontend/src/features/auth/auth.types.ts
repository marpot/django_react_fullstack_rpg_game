export type AuthMode = 'login' | 'register';

export interface AuthFormData {
  username: string;
  email?: string;
  password: string;
}