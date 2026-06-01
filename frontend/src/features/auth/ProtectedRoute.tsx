import React from 'react';
import { Navigate } from 'react-router-dom';

type Props = {
  children: React.ReactNode;
};

const ProtectedRoute: React.FC<Props> = ({ children }) => {
  const token = localStorage.getItem('access_token');

  const isDev = process.env.NODE_ENV === 'development';

  console.log("NODE_ENV:", process.env.NODE_ENV);
  
  if (isDev){
    return <>{children}</>;
  }

  if (!token) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;