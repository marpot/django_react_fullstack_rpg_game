import React from 'react';

interface LoginButtonProps {
  onClick: () => void;
}

const LoginButton: React.FC<LoginButtonProps> = ({ onClick }) => {
  return (
    <button onClick={onClick}>
      Zaloguj
    </button>
  );
};

export default LoginButton;
export{};