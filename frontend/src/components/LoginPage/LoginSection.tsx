import React from "react";
import LoginError from "./LoginError";
import LoginForm from "./LoginForm";

type LoginSectionProps = {
  errorMessage: string;
  onSubmit: (data: { username: string; password: string }) => Promise<void>;
  children?: React.ReactNode;
};

const LoginSection = ({ errorMessage, onSubmit }: LoginSectionProps) => {
  return (
    <section className="login-section">
      {errorMessage && <LoginError errorMessage={errorMessage} />}
      <LoginForm onSubmit={onSubmit} />
    </section>
  );
};

export default LoginSection;
export{};
