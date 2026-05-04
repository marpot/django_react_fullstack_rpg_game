import React, { useState } from 'react';
import { api } from '../api/client'
import { useNavigate, Link } from 'react-router-dom';
import LoginForm from '../components/LoginPage/LoginForm';
import LoginError from '../components/LoginPage/LoginError';

const LoginPage: React.FC = () => {
  const [errorMessage, setErrorMessage] = useState<string>('');
  const navigate = useNavigate();

  const handleSubmit = async ({ username, password }: { username: string; password: string }) => {
    try {
      const response = await api.post(`/accounts/login/`, {
        username,
        password,
      });
      
      console.log('✅ LOGIN OK:', response.data);

      const { access, refresh } = response.data;
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);

      // Add a medieval-style success message
      alert('Witaj, waleczny rycerzu! Masz przed sobą wielką przygodę!');
      
      navigate('/dashboard');
    } catch (error) {
      console.error('❌ Błąd logowania:', error);
      setErrorMessage('Niepoprawna nazwa użytkownika lub hasło');
    }
  };

  return (
    <div className="login-container">
      <div className="background-elements">
        <div className="castle"></div>
      </div>
      
      <section className="section has-background-dark" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <div className="container" style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          {errorMessage && <LoginError errorMessage={errorMessage} />}
          <div className="box has-background-transparent">
            <h1 className="title" style={{ fontSize: 48, fontFamily: 'Playfair Display', color: '#ffd700' }}>Witaj w Średniowiecznym RPG</h1>
            <p className="subtitle" style={{ fontSize: 24, fontFamily: 'Playfair Display', color: '#ffd700' }}>Zaloguj się, aby rozpocząć przygodę</p>
            <LoginForm onSubmit={handleSubmit} />
            <p className="has-text-centered mt-4">
              <Link to="/register" className="has-text-primary">
                Nie masz konta? Zarejestruj się!
              </Link>
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LoginPage;
