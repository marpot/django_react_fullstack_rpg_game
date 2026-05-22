import React, { useState } from 'react';
import TextInput from '../../components/ui/TextInput';
import { api } from '../../api/client';
import Button from 'src/components/ui/Button/Button';

export type AuthMode = 'login' | 'register';

type Props = {
  mode: AuthMode;
  loading?: boolean;
  onSuccess?: () => void;
};

const AuthForm: React.FC<Props> = ({ mode, loading = false, onSuccess }) => {
  const isLogin = mode === 'login';

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    try {
      if (!username || !password) {
        setError('Uzupełnij wymagane pola');
        return;
      }

      if (isLogin) {
        const res = await api.post('/accounts/login/', {
          username,
          password,
        });

        localStorage.setItem('access_token', res.data.access);
        localStorage.setItem('refresh_token', res.data.refresh);

        onSuccess?.();
        return;
      }

      // REGISTER FLOW
      if (!email) {
        setError('Email jest wymagany');
        return;
      }

      await api.post('/accounts/register/', {
        username,
        email,
        password,
      });

      // po rejestracji od razu logujemy UX-friendly flow
      const loginRes = await api.post('/accounts/login/', {
        username,
        password,
      });

      localStorage.setItem('access_token', loginRes.data.access);
      localStorage.setItem('refresh_token', loginRes.data.refresh);

      onSuccess?.();

    } catch (err: any) {
      setError(
        err?.response?.data
          ? JSON.stringify(err.response.data)
          : 'Wystąpił błąd'
      );
    }
  };

  return (
    <form onSubmit={handleSubmit} className="auth-form">

      {error && <div className="form-error">{error}</div>}

      <TextInput
        type="text"
        placeholder="Nazwa użytkownika"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />

      {!isLogin && (
        <TextInput
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      )}

      <TextInput
        type="password"
        placeholder="Hasło"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <Button type="submit" variant="primary" disabled={loading}>
        {loading
          ? 'Ładowanie...'
          : isLogin
            ? 'Zaloguj się'
            : 'Zarejestruj się'}
      </Button>
    </form>
  );
};

export default AuthForm;