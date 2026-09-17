import React from 'react';
import { useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';

interface Props {
  children: React.ReactNode;
}

const MainLayout: React.FC<Props> = ({ children }) => {
  const { pathname } = useLocation();

  const isChroniclesView = [
    '/dashboard',
    '/create-room',
    '/profile',
    '/settings',
  ].includes(pathname);

  return (
    <div className={`app-layout${isChroniclesView ? ' app-layout--chronicles' : ''}`}>
      <aside className="app-sidebar">
        <Sidebar fantasy={isChroniclesView} />
      </aside>

      <main className="app-main">
        {children}
      </main>
    </div>
  );
};

export default MainLayout;