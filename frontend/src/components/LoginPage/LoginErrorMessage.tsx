type Props = {
    message: string;
  };
  
  const LoginErrorMessage = ({ message }: Props) => {
    return <p className="login-error">{message}</p>;
  };
  
  export default LoginErrorMessage;
  export{};
  