import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthForm from '../features/auth/AuthForm';
import '../styles/pages/auth.scss'


const LoginPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="login-page">
      <div className="login-panel">
        <h1 className="login-title">Login</h1>
        <p className="login-subtitle">Zaloguj się do gry</p>

        <AuthForm mode="login" onSuccess={() => navigate('/dashboard')} />

        <div className="login-footer">
          <Link to="/register">Nie masz konta? Zarejestruj się</Link>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;