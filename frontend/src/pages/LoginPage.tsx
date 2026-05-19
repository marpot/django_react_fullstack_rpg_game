import React, { useState } from 'react';
import { api } from '../api/client';
import { useNavigate, Link } from 'react-router-dom';
import LoginForm from '../components/LoginPage/LoginForm';
import LoginError from '../components/LoginPage/LoginError';

import '../components/LoginPage/LoginPage.scss';

const LoginPage: React.FC = () => {
  const [errorMessage, setErrorMessage] = useState<string>('');
  const navigate = useNavigate();

  const handleSubmit = async ({ username, password }: { username: string; password: string }) => {
    try {
      const response = await api.post(`/accounts/login/`, {
        username,
        password,
      });

      const { access, refresh } = response.data;

      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);

      navigate('/dashboard');
    } catch (error) {
      setErrorMessage('Niepoprawna nazwa użytkownika lub hasło');
    }
  };

  return (
    <div className="login-page">

      <div className="login-panel">

        <h1 className="login-title">
          Witaj w Średniowiecznym RPG
        </h1>

        <p className="login-subtitle">
          Zaloguj się, aby rozpocząć przygodę
        </p>

        {errorMessage && <LoginError errorMessage={errorMessage} />}

        <LoginForm onSubmit={handleSubmit} />

        <p className="login-footer">
          <Link to="/register">
            Nie masz konta? Zarejestruj się
          </Link>
        </p>

      </div>
    </div>
  );
};

export default LoginPage;