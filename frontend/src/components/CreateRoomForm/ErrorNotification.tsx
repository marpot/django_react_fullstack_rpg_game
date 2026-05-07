import React from 'react';

const ErrorNotification: React.FC<{ error: string | null; }> = ({ error }) => (
  error ? <div className="notification is-danger">{error}</div> : null
);

export default ErrorNotification; 