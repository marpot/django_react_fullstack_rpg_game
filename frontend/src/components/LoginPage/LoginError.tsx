import React from 'react';

interface LoginErrorProps {
  errorMessage?: string;
}

const LoginError: React.FC<LoginErrorProps> = ({ errorMessage }) => {
  return (
    <div className="has-text-danger" style={{ textAlign: 'center', marginBottom: '1rem' }}>
      {errorMessage}
    </div>
  );
};

export default LoginError;
export{};