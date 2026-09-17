import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

type Props = { fantasy?: boolean };

const Sidebar: React.FC<Props> = ({ fantasy = false }) => {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  const go = (path: string) => {
    navigate(path);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh');
    navigate('/');
  };

  return (
    <nav className="sidebar" aria-label="Nawigacja główna">
      <div className="sidebar-title">
        {fantasy ? (
          <><span>ELDORIA</span><small>CHRONICLES</small></>
        ) : '⚔ Panel Kontrolny'}
      </div>

      <div className="sidebar-nav">
        <button type="button" className={`sidebar-btn${fantasy && pathname === '/dashboard' ? ' is-active' : ''}`} aria-current={pathname === '/dashboard' ? 'page' : undefined} onClick={() => go('/dashboard')}>
          {fantasy ? 'Sala Przygód' : 'Dashboard'}
        </button>

        <button type="button" className={`sidebar-btn${fantasy && pathname === '/profile' ? ' is-active' : ''}`} aria-current={pathname === '/profile' ? 'page' : undefined} onClick={() => go('/profile')}>
          {fantasy ? 'Karta bohatera' : 'Profil'}
        </button>

        <button type="button" className={`sidebar-btn${fantasy && pathname === '/create-room' ? ' is-active' : ''}`} aria-current={pathname === '/create-room' ? 'page' : undefined} onClick={() => go('/create-room')}>
          {fantasy ? 'Nowa wyprawa' : 'Twórz pokój'}
        </button>

        <button type="button" className="sidebar-btn" onClick={() => go('/settings')}>
          Ustawienia
        </button>

        <button type="button" className="sidebar-btn danger" onClick={logout}>
          Wyloguj się
        </button>
      </div>
    </nav>
  );
};

export default Sidebar;
