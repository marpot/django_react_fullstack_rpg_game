import React, { useState } from 'react';
import { api } from '../api/client';
import { Link, useNavigate } from 'react-router-dom';

import '../components/RegisterPage/RegisterPage.scss';
import TextInput from '../components/ui/TextInput';

const RegisterPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const data = { username, email, password };

    try {
      const response = await api.post('/accounts/register/', data);

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
    <div className="register-page">
      <div className="register-panel">

        <h1 className="register-title">Rejestracja</h1>

        <p className="register-subtitle">
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
            required
          />

          <TextInput
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <TextInput
            type="password"
            placeholder="Hasło"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button className="btn-primary" type="submit">
            Zarejestruj się
          </button>

        </form>

        <div className="register-footer">
          <Link to="/">Masz już konto? Zaloguj się</Link>
        </div>

      </div>
    </div>
  );
};

export default RegisterPage;