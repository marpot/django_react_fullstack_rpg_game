import React from 'react';
import AuthForm from '../features/auth/AuthForm';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/pages/auth.scss';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="login-page login-page--entry">
      <main className="login-entry">
        <header className="login-brand">
          <p className="login-brand__name">ELDORIA</p>
          <p className="login-brand__tagline">Twoja historia zaczyna się tutaj</p>
        </header>

        <section className="login-panel login-panel--entry" aria-labelledby="register-heading">
          <h1 className="login-title" id="register-heading">Stwórz swoją postać</h1>
          <p className="login-subtitle">
            Dołącz do świata Eldorii i rozpocznij swoją przygodę.
          </p>

          <AuthForm mode="register" onSuccess={() => navigate('/')} />

          <div className="login-footer">
            <span>Masz już konto?</span>
            <Link to="/">Zaloguj się</Link>
          </div>
        </section>
      </main>
    </div>
  );
};

export default RegisterPage;
