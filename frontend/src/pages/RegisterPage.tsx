import React, { useState } from 'react';
import api from '../axiosConfig';
import { Link, useNavigate } from 'react-router-dom';

interface RegisterPageProps {
  
}

interface RegisterPageState {
  username: string;
  email: string;
  password: string;
  message: string;
  error: string;
}

const RegisterPage: React.FC<RegisterPageProps> = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const data = {
      username,
      email,
      password
    };

    try {
      const response = await api.post('/accounts/register/', data);
      if (response.status >= 200 && response.status < 300) {
        setMessage('Rejestracja zakończona sukcesem!');
        setError('');

        setTimeout(() => navigate('/login'), 1000);
      } 
    } catch (err: any) {
        console.error('REGISTER ERROR:', err);

        const msg =
        err?.response?.data
          ? JSON.stringify(err.response.data)
          : 'Nieznany błąd';

    setError('Błąd rejestracji: ' + msg);
    setMessage('');
    }
  }
  return (
    <div>
      <section className="section">
        <div className="container">
          <h1 className="title has-text-centered">Rejestracja</h1>
          {message && <p style={{ color: 'green' }}>{message}</p>}
          {error && <p style={{ color: 'red' }}>{error}</p>}
          
          <form onSubmit={handleSubmit}>
            {/* Pole użytkownika */}
            <div className="field">
              <label className="label" htmlFor="username">Nazwa użytkownika:</label>
              <div className="control">
                <input
                  className="input"
                  type="text"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
            </div>

            {/* Pole email */}
            <div className="field">
              <label className="label" htmlFor="email">Email:</label>
              <div className="control">
                <input
                  className="input"
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            {/* Pole hasła */}
            <div className="field">
              <label className="label" htmlFor="password">Hasło:</label>
              <div className="control">
                <input
                  className="input"
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            {/* Przycisk */}
            <div className="field">
              <div className="control">
                <button className="button is-primary is-fullwidth" type="submit">
                  Zarejestruj się
                </button>
              </div>
            </div>

          	<div className="field has-text-centered">
            	<p>Masz już konto? <Link to="/">Zaloguj się</Link></p>
          	</div>
          </form>
        </div>
      </section>
    </div>
  );
};

export default RegisterPage;
