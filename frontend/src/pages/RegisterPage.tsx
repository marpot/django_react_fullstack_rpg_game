import React from 'react';
import LoginForm from '../features/auth/AuthForm';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/pages/auth.scss';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="login-page">
      <div className="login-panel">
        <h1 className="login-title">Rejestracja</h1>
        <p className="login-subtitle">Stwórz konto</p>

        <LoginForm mode="register" onSuccess={() => navigate('/')} />
        <div className="register-footer">
          <Link to="/">Masz już konto? Zaloguj się</Link>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;