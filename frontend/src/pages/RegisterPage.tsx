import React, { useState } from 'react';
import { api } from '../api/client';
import { Link, useNavigate } from 'react-router-dom';

import '../components/RegisterPage/RegisterPage.scss';
import TextInput from 'src/components/ui/TextInput';

const RegisterPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    try {
      const response = await api.post('/accounts/register/', {
        username,
        email,
        password,
      });

      if (response.status >= 200 && response.status < 300) {
        setMessage('Rejestracja zakończona sukcesem!');
        setError('');

        setTimeout(() => navigate('/'), 1000);
      }
    } catch (err: any) {
      const msg = err?.response?.data
        ? JSON.stringify(err.response.data)
        : 'Nieznany błąd';

      setError('Błąd rejestracji: ' + msg);
      setMessage('');
    }
  };

  return (
    <div className="register-page login-page">
      <div className="register-panel login-panel">

        <h1 className="login-title">Rejestracja</h1>

        <p className="login-subtitle">
          Stwórz konto i rozpocznij przygodę
        </p>

        {message && <p className="form-success">{message}</p>}
        {error && <p className="form-error">{error}</p>}

        <form onSubmit={handleSubmit}>

          <TextInput
            type="text"
            placeholder="Nazwa użytkownika"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <TextInput
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <TextInput
            type="password"
            placeholder="Hasło"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button className="btn-primary" type="submit">
            Zarejestruj się
          </button>

        </form>

        <p className="login-footer">
          Masz już konto? <Link to="/">Zaloguj się</Link>
        </p>

      </div>
    </div>
  );
};

export default RegisterPage;