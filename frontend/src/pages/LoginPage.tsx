import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthForm from '../features/auth/AuthForm';
import '../styles/pages/auth.scss'


const LoginPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="login-page login-page--entry">
      <main className="login-entry">
        <header className="login-brand">
          <p className="login-brand__name">ELDORIA CHRONICLES</p>
          <p className="login-brand__tagline">Twoja historia zaczyna się tutaj</p>
        </header>

        <section className="login-panel login-panel--entry" aria-labelledby="login-heading">
          <h1 className="login-title" id="login-heading">Witaj, Wędrowcze</h1>
          <p className="login-subtitle">
            Zaloguj się, aby kontynuować swoją podróż w świecie pełnym przygód.
          </p>

          <AuthForm mode="login" onSuccess={() => navigate('/dashboard')} />

          <div className="login-footer">
            <span>Nie masz jeszcze konta?</span>
            <Link to="/register">Stwórz swoją postać</Link>
          </div>
        </section>
      </main>
    </div>
  );
};

export default LoginPage;
