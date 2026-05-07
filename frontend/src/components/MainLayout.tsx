import React from 'react';
import Sidebar from './Sidebar';

interface Props {
  children: React.ReactNode;
}

const MainLayout: React.FC<Props> = ({ children }) => {
  return (
    <div className="columns">
      <div className="column is-one-fifth">
        <Sidebar />
      </div>
      <div className="column">
        {children}
      </div>
    </div>
  );
};

export default MainLayout;