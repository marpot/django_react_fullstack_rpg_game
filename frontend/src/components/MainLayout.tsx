import React from 'react';
import Sidebar from './Sidebar';

interface Props {
  children: React.ReactNode;
}

const MainLayout: React.FC<Props> = ({ children }) => {
  return (
    <div className="app-layout">
      <aside className="app-sidebar">
        <Sidebar />
      </aside>

      <main className="app-main">
        {children}
      </main>
    </div>
  );
};

export default MainLayout;