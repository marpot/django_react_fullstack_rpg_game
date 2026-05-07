import React, { useState } from 'react';

interface LoginFormProps {
  onSubmit: (data: { username: string; password: string }) => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onSubmit }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!username || !password) {
      setError('Wpisz nazwę użytkownika i hasło');
      return;
    }
    onSubmit({ username, password });
  };

  return (
    <form onSubmit={handleSubmit} className="form">
      {error && <p className="has-text-danger">{error}</p>}
      <div className="field">
        <label className="label">Nazwa użytkownika</label>
        <div className="control">
          <input
            className="input"
            type="text"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />
        </div>
      </div>

      <div className="field">
        <label className="label">Hasło</label>
        <div className="control">
          <input
            className="input"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>
      </div>

      <div className="field">
        <div className="control">
          <button type="submit" className="button">
            Zaloguj się
          </button>
        </div>
      </div>
    </form>
  );
};

export default LoginForm;
export{};
